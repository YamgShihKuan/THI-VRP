## 論文演算法
### 基本架構為一開始先讀取資料，根據乘客訂單指派可服務車輛，將所有訂單指派完畢後，每台車會有行駛路線亦即派車單，而在建立好行駛路線後，必須經過improvement及等待時間的調整，最後輸出派車單，派車單包含在送乘客的時間、地點、身分及順序，司機可以按照派車單的順序接送客人。

* sql server seting：sql server、database、使用者名稱、密碼等基礎設定。
* parameter setting：常數項設定，包含最大旅行距離、上下車服務時間、時窗、最大旅行時間等
* input three sql data sheet：將sql中的乘客訂單、司機名單及成本矩陣讀去盡python
* datafit：轉換sql資料格式的函式
* main_funtion：主要函式
  * time_form：
  * total_time：
  * total_distant：
  * route_seed_initialer：
  * route_seed_initialer2：
  * check_feasible_route：
  * regret_insert：
  * relocation_operator：
  * exchange_operator：
  * check_service_time：
  * check_arrive_time：
  * ride_counter：
* sql cost：
* sql request：
* sql resource：
* generate the initial route：
* show the initial result：
* improvement the initial route：
* show the improved result：
* show the unservable result：
* waiting strategy & Fix TW：
* calculate the trip & format the data：
* Data Input and Data Ouput：

![image](https://github.com/YangShihKuan/THI-VRP-thesis/blob/master/%E7%A8%8B%E5%BC%8F%E7%B5%90%E6%A7%8B.PNG)
