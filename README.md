## 論文演算法
### 基本架構為一開始先讀取資料，根據乘客訂單指派可服務車輛，將所有訂單指派完畢後，每台車會有行駛路線亦即派車單，而在建立好行駛路線後，必須經過improvement及等待時間的調整，最後輸出派車單，派車單包含在送乘客的時間、地點、身分及順序，司機可以按照派車單的順序接送客人。

* **sql server seting**：sql server、database、使用者名稱、密碼等基礎設定。
* **parameter setting**：常數項設定，包含最大旅行距離、上下車服務時間、時窗、最大旅行時間等
* **input three sql data sheet**：將sql中的乘客訂單、司機名單及成本矩陣讀去盡python
* **datafit**：轉換sql資料格式的函式
* **main_funtion**：主要函式
  >* **time_form**：專換時間為整數
  >* **total_time**：計算路線總旅行時間
  >* **total_distant**：計算路線總旅行距離
  >* **route_seed_initialer**：初始化乘客方法一
  >* **route_seed_initialer2**：初始化乘客方法二
  >* **check_feasible_route**：檢查路線時窗是否滿足限制式，包含乘客時窗、車輛容量、司機營運時間等等
  >* **regret_insert**：本研究所採用的一種演算法，會計算每次插入點的最小機會成本，並以該位置作為插入位置
  >* **relocation_operator**：改善初始路線方法一
  >* **exchange_operator**：改善初始路線方法一
  >* **check_service_time**：輸出車輛實際服務時間點
  >* **check_arrive_time**：輸出車輛實際抵達時間點
  >* **ride_counter**：將現有路線中的乘客分類集中成趟次
  * **sql cost**：設定成本資料格式
  * **sql request**：設定需求資料格式
  * **sql resource**：設定資源資料格式
  * **generate the initial route**：產生初始路線
  * **show the initial result**：展示初始路線
  * **improvement the initial route**：改善初始路線
  * **show the improved result**：展示改善路線
  * **show the unservable result**：展示未服務訂單
  * **waiting strategy & Fix TW**：等待時間調整及固調好時窗
  * **calculate the trip & format the data**：計算趟次及將資料轉換成所需格式
* **Data Input and Data Ouput**：輸出資料至sql

#### 實際如下圖：
![image](https://github.com/YangShihKuan/THI-VRP-thesis/blob/master/%E7%A8%8B%E5%BC%8F%E7%B5%90%E6%A7%8B.PNG)
