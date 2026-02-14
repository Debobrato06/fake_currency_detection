# Detection of Fake Bank Currency with Machine Learning Algorithms

**Authors:** Debobrato Das$^{1*}$, Abcd E. Ghij$^{2}$, Klmn Opqr$^{2,3}$, and Stuv Wx Yz$^{4}$  
$^{1}$Department of Software Engineering, Daffodil International University, Dhaka, Bangladesh. [Your Email Address]  
$^{2}$[Name of Institution, Country] [Email Address]  
$^{3}$[Name of Institution, Country] [Email Address]  
$^{4}$[Name of Institution, Country] [Email Address]  
*Correspondence: [Your Email Address]

**Received:** 14 February 2026; **Accepted:** XX Month 20XX; **Published:** XX Month 20XX

---

### Abstract
The rapid advancement in printing and scanning technologies has led to an increase in counterfeit currency production, posing a significant challenge for financial institutions and economies. Existing banknote authentication systems, though effective, are often prohibitively expensive, limiting their accessibility. This research presents a cost-effective, accurate, and reliable approach for detecting counterfeit banknotes using machine learning and image processing techniques. The proposed system extracts and analyzes key currency features, such as micro-printing, watermarks, and ultraviolet (UV) lines, by leveraging Optical Character Recognition (OCR), Face Recognition, and the Canny Edge Detection along with the Hough Transformation Algorithm. The system compares extracted features of suspected banknotes with genuine currency templates to determine authenticity. The model's efficiency and accuracy were tested using the Bangladeshi 1000 Taka note, ensuring its practical applicability. The proposed solution emphasizes affordability, scalability, and ease of deployment, making it suitable for both large financial institutions and smaller businesses. Through rigorous experimentation, the system demonstrated high reliability and precision, achieving a combined accuracy of 93.33%.

**Keywords:** Digital Image Processing; Counterfeit Detection; Fake Currency; OCR; Canny Edge Detection; Hough Transformation.

---

## 1. Introduction
Counterfeit currency has been a significant issue ever since the inception of monetary systems. From the ancient days of coinage, counterfeiters have devised methods to deceive merchants and governments alike, altering the value of currency for personal gain. The first counterfeiting attempts involved scraping precious metals from genuine coins, only to reapply them to lower-value metals, creating forged currency. As time progressed, counterfeiters continued to refine their techniques, adapting to the evolving nature of money. The development of paper currency and coins as we know them today introduced new challenges and prompted the creation of increasingly sophisticated anti-counterfeiting measures.

Despite advancements in currency security features such as holograms, watermarks, and security threads, counterfeiting remains a pervasive problem globally. The increasing availability and affordability of technologies like inkjet printers and scanners have enabled counterfeiters to reproduce high-quality fake notes at a fraction of the cost of traditional methods. According to recent reports [1], counterfeiting is on the rise due to the low cost and widespread availability of printing devices, which allow individuals to create counterfeit notes in their own homes. 

Given the widespread issue of counterfeit currency and the limitations of existing detection systems, there is an urgent need for more efficient and cost-effective methods to identify fake banknotes. This paper proposes a solution by employing machine learning and image processing algorithms. By leveraging OCR, Face Recognition, Canny Edge Detection, and the Hough Transformation Algorithm, the proposed system offers a low-cost, efficient, and reliable alternative for detecting counterfeit banknotes.

### 1.1 Motivation
The motivation for this research arises from the pressing need to combat the growing prevalence of counterfeit currency, which continues to harm economies worldwide. The increasing sophistication of counterfeit techniques challenges traditional detection systems, making them increasingly unreliable. As the Federal Reserve has noted, "Counterfeit currency is a growing issue that not only causes financial loss to individuals and businesses but also undermines confidence in a nation's monetary system" [4].

In DEVELOPING countries like Bangladesh, where the circulation of counterfeit currency is a significant problem, low-cost and efficient solutions are critical. The International Monetary Fund (IMF) has emphasized that "developing nations are particularly vulnerable to counterfeit currency because of limited access to reliable detection systems" [9].

### 1.2 Objectives
The primary objectives of this research are:
*   To detect fake notes using Optical Character Recognition (OCR).
*   To detect fake notes using Face Recognition.
*   To detect fake notes using Hough Transformation.
*   To develop an integrated algorithm that combines multiple detection methods for optimal results.
*   To evaluate and analyze the performance differences across these various methods.

### 1.3 Contribution Summary
The key contributions of this work include:
*   An integrated framework combining OCR, face recognition, and Hough Transformation for enhanced counterfeit detection.
*   Achieving a high accuracy of 93.33% through the ensemble of multi-feature detection.
*   Development of a scalable system suitable for deployment in banks and small businesses.
*   Validation of the proposed model on real-world datasets of Bangladeshi currency.

## 2. Literature Review
This section provides an overview of existing research and methodologies in counterfeit currency detection.

**2.1.1 Mohana et al. (2019):** Focused on extracting texture and edge features using Wavelet Transforms and Gray-Level Co-occurrence Matrix (GLCM). The method achieved 98% accuracy but required high computational resources [10].

**2.1.2 Rao et al. (2020):** Applied Random Forest to classify fake and real banknotes using image intensity and texture features. This study demonstrated 96% accuracy on Indian currency [11].

**2.1.3 Singh et al. (2020):** Examined SVM, KNN, and Decision Trees in conjunction with image preprocessing. Achieving 94% accuracy, the study underscored the importance of preprocessing [12].

**2.1.4 Ali et al. (2021):** Introduced CNNs for detecting counterfeit currency, achieving 97.5% accuracy by learning visual features automatically from raw data [13].

**2.1.5 Das et al. (2022):** Proposed a hybrid CNN-SVM model that achieved 99% accuracy on European banknotes by combining feature extraction and high-dimensional classification [14].

## 3. Methodology
This section details the individual components of the proposed system.

### 3.1 OCR (Optical Character Recognition)
OCR is used to recognize printed text on banknotes, specifically serial numbers and security codes. 
1.  **Preprocessing:** Noise reduction and binarization.
    $$I_{binarized}(x,y) = \begin{cases} 255 & \text{if } I(x,y) > T \\ 0 & \text{if } I(x,y) \le T \end{cases}$$
2.  **Segmentation & Recognition:** Characters are segmented and identified comparing against genuine templates.

### 3.2 Face Recognition
Applied to detect watermarks and printed portraits. 
1.  **Feature Extraction:** Uses Eigenfaces or LBP to extract facial characteristics.
2.  **Similarity Measurement:** Calculated via Euclidean distance:
    $$d = \sqrt{\sum_{i=1}^{n} (x_i - y_i)^2}$$

### 3.3 Hough Transformation
Used for detecting geometric security features like lines and borders. 
- **Mapping:** Maps Cartesian coordinates $(x,y)$ to polar space $(\rho, \theta)$:
    $$\rho = x \cos(\theta) + y \sin(\theta)$$

### 3.4 Proposed Integrated Model
The proposed model integrates OCR, Face Recognition, and Hough Transformation. The workflow involves:
1.  **Acquisition:** Capture image via camera/scanner.
2.  **Multimodal Analysis:** Running the three detection modules in parallel.
3.  **Decision Logic:** Aggregating results to provide a final authenticity verdict.

## 4. Implementation
The system was implemented using Python, OpenCV, and MATLAB for algorithm testing.
*   **Data Collection:** 30 high-resolution images of Bangladeshi 1000 Taka notes.
*   **Preprocessing:** Denoising, rotation correction, and grayscale conversion.
*   **Hardware:** 16-megapixel camera with macro lens for micro-printing detail.

## 5. Experimental Results and Analysis
Performance was evaluated based on individual and combined algorithms.

**Table 1: Performance Comparison of Detection Methods**
| Method | Correct Readings | Total Runs | Accuracy (%) | Avg. Run Time (s) |
| :--- | :--- | :--- | :--- | :--- |
| OCR | 22 | 30 | 73.33% | 3.61 |
| Hough Transformation | 24 | 30 | 80.00% | 4.29 |
| Face Recognition | 23 | 30 | 76.67% | 5.37 |
| **Proposed Integrated Model** | **28** | **30** | **93.33%** | **6.19** |

*Note: Individual accuracies for OCR, Face Recognition, and Hough Transform were 73.33%, 76.67%, and 80% respectively. The combined model significantly improved reliability to 93.33%.*

## 6. Conclusion
This research successfully developed an integrated system for counterfeit currency detection using a combination of OCR, Face Recognition, and Hough Transformation. While individual techniques showed moderate success, their integration provided a robust detection rate of 93.33%. This approach offers a cost-effective solution for financial security in developing economies, ensuring high reliability with minimal hardware requirements. Future work will focus on integrating deep learning models for even higher precision.

## CRediT Author Contribution Statement
**Debobrato Das:** Conceptualization, Methodology, Software, Investigation, Writing - Original Draft. **Abcd E. Ghij:** Supervision, Writing - Review & Editing. **Klmn Opqr:** Validation, Resources. **Stuv Wx Yz:** Project administration.

## Acknowledgement
We would like to thank the Department of Software Engineering at Daffodil International University for providing the necessary facilities and support for this research. Special thanks to the Bangladesh Bank for providing currency samples for testing.

## References
[1] (Reference from thesis...)  
[4] Federal Reserve (2020). *Counterfeit Currency Issues*.  
[9] IMF (2019). *Security in Developing Nations*.  
[10] Mohana, R. et al. (2019). *International Journal of Computer Applications*.  
[11] Rao, A. et al. (2020). *Journal of Financial Studies*.  
[12] Singh, R. et al. (2020). *Journal of Financial Technology*.  
[13] Ali, H. et al. (2021). *IEEE Transactions on Neural Networks*.  
[14] Das, M. et al. (2022). *Journal of Computer Vision*.
