
# InitVerse Auto trading Mainnet Bot  

## Getting Started  

### Prerequisites  

1. **Create an Account on InitVerse**  
   - Visit [InitVerse Candy]([https://candy.inichain.com/](https://candy.inichain.com?invite=0x064Af2B49111642ED5AaC9B0Ea655f056AB03d7B) and connect your wallet.  
   - Link your social accounts and complete the "Start Here" task.  
   - Join the [miner pool](https://inichain.gitbook.io/initverseinichain/inichain/mining-mainnet) with the operating system of your choice (Windows/Linux).  
   - Acquire INI tokens by mining or receiving them from someone.  

### Setup  

Follow these steps to set up and run the bot.  

#### 1. Clone the Repository  
```bash
git clone https://github.com/jeripangestu/Initverse-trading.git
cd InitVerse-bot
```

#### 2. Create and Activate a Virtual Environment  

**Windows:**  
```bash
python -m venv venv
venv\init\activate
```

**Linux/Mac:**  
```bash
python3 -m venv venv
source init/bin/activate
```

#### 3. Install Dependencies  
```bash
pip install -r requirements.txt
```

#### 4. Configure the Bot  
input your private key to  `pk.txt` file in the project directory with the following structure:  
```json
your_private_key1
your_private_key2
your_private_key3
your_private_key4
your_private_key5
```
Replace `your_private_key1` and `your_private_key2` with your actual private keys.  

#### 5. Run the Bot  
```bash
python main.py
```
Credits: @Anzywiz
