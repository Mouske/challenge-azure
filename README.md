# challenge-azure
# 🚄 iRail Data Pipeline – Azure Deployment

This project is a real-time data pipeline that fetches train departure data from the public [iRail API](https://api.irail.be/), normalizes it, and stores it in an Azure-hosted SQL database.

---

## 📌 Objectives

- 🔁 Regularly fetch train departures from iRail API.
- 🧼 Clean and normalize the retrieved data.
- 🗄️ Store the data in an **Azure SQL Database**.
- ☁️ Automate the pipeline using **Microsoft Azure services**.

---

## 🧰 Tech Stack

| Component         | Technology                     |
|------------------|---------------------------------|
| Data Source       | [iRail API](https://api.irail.be/) |
| Data Processing   | Python (requests, pandas)       |
| Data Storage      | Azure SQL Database              |
| Deployment        | Azure Functions *(or Docker + Azure Container Instance)* |
| Scheduling        | Azure Timer Trigger / Logic App |

---
