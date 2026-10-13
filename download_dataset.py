"""
Download the JaalTaka dataset (genuine + counterfeit Bangladeshi banknotes).

Source : https://data.mendeley.com/datasets/2m7wk5cy4c  (CC BY 4.0)
Paper  : JaalTaka: A benchmark dataset for detecting counterfeit Bangladeshi
         banknotes, Data in Brief (2025), doi:10.1016/j.dib.2025.112377

The original zip is ~7.6 GB. Instead of saving it to disk, this script reads the
zip remotely with HTTP range requests, fetches each image in parallel, resizes it
(longest side = --max-side) and stores it as:

    data/jaaltaka/real/note_001_1.jpg ... note_802_6.jpg
    data/jaaltaka/fake/note_001_1.jpg ... note_588_6.jpg

The script is resumable: already-saved images are skipped.

Usage:
    python download_dataset.py [--out data/jaaltaka] [--workers 16] [--max-side 1024]
"""
import argparse
import io
import os
import struct
import subprocess
import sys
import time
import urllib.request
import zlib
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

from PIL import Image

ZIP_URL = ("https://data.mendeley.com/public-files/datasets/2m7wk5cy4c/files/"
           "27e6e73f-407a-42ea-966c-1d669a3a41d9/file_downloaded")
CLASS_DIRS = {"real_notes": "real", "fake_notes": "fake"}


def resolve_url():
    """Follow the Mendeley redirect to the S3 object and return (url, size)."""
    loc = subprocess.check_output(
        ["curl", "-s", "-o", os.devnull, "-w", "%{redirect_url}", ZIP_URL], text=True).strip()
    if not loc:
        loc = ZIP_URL
    r = urllib.request.urlopen(urllib.request.Request(loc, headers={"Range": "bytes=0-0"}), timeout=60)
    return loc, int(r.headers["Content-Range"].split("/")[1])


def fetch(url, start, end, retries=6):
    """Fetch bytes [start, end] (inclusive) with retries."""
    req = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}"})
    err = "short read"
    for attempt in range(retries):
        try:
            data = urllib.request.urlopen(req, timeout=180).read()
            if len(data) == end - start + 1:
                return data
        except Exception as e:  # network hiccup -> retry
            err = e
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"range {start}-{end} failed: {err}")


class RangeFile(io.RawIOBase):
    """Minimal seekable file over HTTP range requests (used only to read the central directory)."""

    def __init__(self, url, size):
        self.url, self.size, self.pos = url, size, 0

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        self.pos = off if whence == 0 else (self.pos + off if whence == 1 else self.size + off)
        return self.pos

    def readinto(self, b):
        n = min(len(b), self.size - self.pos)
        if n <= 0:
            return 0
        data = fetch(self.url, self.pos, self.pos + n - 1)
        b[:n] = data
        self.pos += n
        return n


def extract_member(url, info):
    """Download one zip member and return its decompressed bytes."""
    # local header (30 bytes) + name + extra; extra length may differ from the central directory
    margin = 30 + len(info.filename.encode()) + 1024
    raw = fetch(url, info.header_offset, info.header_offset + margin + info.compress_size - 1)
    sig, *_, name_len, extra_len = struct.unpack("<IHHHHHIIIHH", raw[:30])
    assert sig == 0x04034B50, "bad local header"
    start = 30 + name_len + extra_len
    payload = raw[start:start + info.compress_size]
    if info.compress_type == zipfile.ZIP_STORED:
        return payload
    if info.compress_type == zipfile.ZIP_DEFLATED:
        return zlib.decompress(payload, -15)
    raise ValueError(f"unsupported compression {info.compress_type}")


def save_resized(data, path, max_side):
    im = Image.open(io.BytesIO(data))
    im = im.convert("RGB")
    im.thumbnail((max_side, max_side), Image.LANCZOS)
    tmp = path + ".part"
    im.save(tmp, "JPEG", quality=92)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/jaaltaka")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--max-side", type=int, default=1024)
    args = ap.parse_args()

    url, size = resolve_url()
    print(f"Remote zip: {size / 1e9:.2f} GB")
    with zipfile.ZipFile(RangeFile(url, size)) as z:
        members = [i for i in z.infolist() if not i.is_dir() and i.filename.lower().endswith((".jpg", ".jpeg", ".png"))]

    jobs = []
    for info in members:
        top = info.filename.split("/")[0]
        if top not in CLASS_DIRS:
            continue
        dst_dir = os.path.join(args.out, CLASS_DIRS[top])
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, os.path.splitext(os.path.basename(info.filename))[0] + ".jpg")
        if not os.path.exists(dst):
            jobs.append((info, dst))
    print(f"{len(members)} images in zip, {len(jobs)} still to download")

    done, failed, t0 = 0, [], time.time()

    def work(job):
        info, dst = job
        save_resized(extract_member(url, info), dst, args.max_side)
        return info.compress_size

    nbytes = 0
    with ThreadPoolExecutor(args.workers) as ex:
        futs = {ex.submit(work, j): j for j in jobs}
        for f in as_completed(futs):
            try:
                nbytes += f.result()
                done += 1
            except Exception as e:
                failed.append((futs[f][0].filename, str(e)))
            if (done + len(failed)) % 100 == 0:
                el = time.time() - t0
                print(f"  {done}/{len(jobs)} done, {len(failed)} failed, "
                      f"{nbytes / el / 1e6:.2f} MB/s, elapsed {el / 60:.1f} min", flush=True)

    print(f"Finished: {done} saved, {len(failed)} failed")
    for name, err in failed[:20]:
        print("  FAILED", name, err)
    if failed:
        print("Re-run the script to retry failed images.")
        sys.exit(1)


if __name__ == "__main__":
    main()
