# **問題一**  

*如果要達成「能夠預測指定的symbol在90天後，是否有成長10%」的目標，會選用的模型及訓練方式，文字提供選用的模型及原因。*  

## **模型選擇**  
經過對財務分析與機器學習應用的研究，我選擇 XGBoost 的 **XGBClassifier**，其以下特性非常適合本問題：  

### **1. 適合股價走向分析**  
- 能處理「時間序列問題」與「分類問題」  

### **2. 適合小型資料集**  
- 由於我們的資料集不大，傳統機器學習模型比深度學習更適合  
- Decision tree-based 模型不需要大量數據即可有效訓練  
- 內建 L1 / L2 regularization，可防止小資料集 overfit  

### **3. 商業價值**  
- 支援 GPU 平行運算，但也可在 CPU 訓練，部署與維護更容易  
- 訓練時間短，可快速測試不同參數，符合金融市場變動需求  
- 支援 Incremental Learning，能隨新數據更新模型，而不必重新訓練整個模型  

## **模型訓練方式**  

### **1. 定義 Label**  
- 由於題目未明確定義「成長」，故先選擇季度數據的 revenue growth 為指標  
- 成長 > 10% 設為 1，否則為 0  

### **2. 第一次 Feature Engineering**  
- 使用 Correlation Analysis 過濾與 Label 幾乎無關的變數  

### **3. Data Splitting**  
- 8:2 切割為 training set 與 testing set  
- 不可 shuffle，需依時間順序切割  

### **4. 訓練 Base Model**  
- 以初步篩選後的變數訓練 XGBClassifier  

### **5. 第二次 Feature Engineering**  
- 使用 XGBoost 的 Feature Importance 篩選影響預測最顯著的變數  

### **6. 重新訓練模型**  
- 用篩選後的特徵再訓練一個 XGBClassifier  

### **7. Hyperparameter Tuning**  
- 由於資料集小，可選擇 Bayesian Optimization 或 Grid Search  

### **8. 定期更新模型 (Incremental Learning)**  
- 隨著新數據進入，利用 Incremental Learning 進行模型更新  
  
---
  
# **問題二**

*在訓練中如何從現有的資料集提取出關鍵影響欄位?*

我們可以使用兩階段 feature engineering 來提取出關鍵欄位，具體模型訓練步驟可參照上一題。第一階段，先計算每個變數與 label 之間的 Pearson correlation 或 Spearman correlation，去除相關性過低或過高的特徵。第二階段 (訓練完 Base Model 後)，使用 XGBoost 內建的 Feature Importance 計算功能，刪除影響較低的變數。
  
---
  
# **問題三**

*如何利用目前已有的資料集欄位，推論出更有效的新資料欄位?*

目前的資料集中的技術指標欄位很分散，因此可以考慮轉換成：

* **變化率：** 變化率可以幫助模型捕捉趨勢變化的速度，例如，```RSI\_5\_change \= RSI\_5(t) \- RSI\_5(t-1)```。RSI 短時間內的劇烈變化，可能預示著價格即將反轉或延續趨勢  
* **移動均線交叉：** 均線交叉（如黃金交叉、死亡交叉）表示短期趨勢與長期趨勢的關係，能幫助模型判斷市場趨勢是否轉向。例如，```Crossover\_5\_20 \= 1 if SMA\_5 \> SMA\_20 else 0```
