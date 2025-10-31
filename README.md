# 🚰 Pharos Atlantic Faucet Auto Bot

Automated bot for claiming and transferring tokens from Pharos Atlantic Faucet with multi-threading support and proxy rotation.

## ✨ Features

- 🤖 **Automated Faucet Claiming**: Automatically claims tokens from Pharos Atlantic Faucet
- 🔄 **Auto Transfer**: Automatically transfers claimed tokens to your specified address
- 🧵 **Multi-threading Support**: Run multiple jobs simultaneously for faster processing
- 🌐 **Proxy Support**: Rotate between multiple proxies to avoid rate limiting
- 🔐 **reCAPTCHA Solving**: Integrated with 2captcha.com for automatic CAPTCHA solving
- 📊 **Beautiful Logs**: Colorful and organized terminal output with timestamps
- 💾 **External Configuration**: API keys and addresses loaded from external files
- 📈 **Progress Tracking**: Real-time progress monitoring and success rate statistics

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

## 🚀 Installation

1. Clone this repository:
```bash
git clone https://github.com/febriyan9346/Pharos-Atlantic-Faucet.git
cd Pharos-Atlantic-Faucet
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### 1. Create `2captcha.txt` file:
```
YOUR_2CAPTCHA_API_KEY
```
Get your API key from [2captcha.com](https://2captcha.com)

### 2. Create `address.txt` file:
```
0xYourRecipientAddressHere
```
This is the address where all claimed tokens will be sent.

### 3. Create `proxy.txt` file (optional):
```
http://proxy1:port
http://proxy2:port
socks5://proxy3:port
```
One proxy per line. If no proxies are provided, the bot will run without proxy rotation.

## 📝 File Structure

```
pharos-faucet-bot/
│
├── bot.py              # Main bot script
├── requirements.txt    # Python dependencies
├── 2captcha.txt       # Your 2captcha API key
├── address.txt        # Your recipient address
├── proxy.txt          # List of proxies (optional)
└── README.md          # This file
```

## 🎮 Usage

1. Make sure all configuration files are properly set up
2. Run the bot:
```bash
python bot.py
```

3. Enter the number of loops (jobs) you want to run
4. Enter the number of threads (parallel jobs)
5. Watch the magic happen! ✨

## 📊 Example Output

```
[10:30:45] ✅ Connected to RPC
[10:30:45] ✅ API Key loaded from 2captcha.txt
[10:30:45] ✅ Recipient address loaded: 0x1d1aFC2d015963017bED1De13e4ed6c3d3ED1618
[10:30:45] ✅ Loaded 5 proxies

📢 Enter number of loops: 10
🧵 Enter number of threads: 3

🚀 Starting 10 jobs with 3 threads...

[10:30:50] [Job  1/10] 🚀 Starting job...
[10:30:50] [Job  1/10] 🔑 From: 0xabc...
[10:30:50] [Job  1/10] 🎯 To: 0x1d1...
[10:30:55] [Job  1/10] ✅ Recaptcha Solved
[10:30:55] [Job  1/10] 💧 Requesting faucet...
[10:31:00] [Job  1/10] ✅ Faucet success!
[10:31:05] [Job  1/10] 💰 Balance: 0.100000 PHRS
[10:31:10] [Job  1/10] 🎉 Transfer Successful!

📊 Progress: 10/10 (100.0%) | Success: 8

==================================================================
                    📊 FINAL SUMMARY
==================================================================
✅ Total Success    : 8
📢 Total Jobs       : 10
❌ Failed Jobs      : 2
📊 Success Rate     : 80.00%
⏱️  Duration        : 180.45 seconds
⚡ Average per job  : 18.05 seconds
==================================================================
```

## 🔧 Advanced Configuration

You can modify these variables in `bot.py`:

- `RPC_URL`: The RPC endpoint for Pharos Atlantic
- `EXPLORER`: Block explorer URL
- `CAPTCHA_API`: CAPTCHA service API endpoint (2captcha or capmonster)
- `PAGE_URL`: Faucet website URL
- `SITE_KEY`: reCAPTCHA site key

## ⚠️ Important Notes

- Make sure you have sufficient balance in your 2captcha account
- The bot generates a new wallet for each claim attempt
- Each wallet's full balance (minus gas fees) is transferred to your recipient address
- Use proxies if you're running many jobs to avoid rate limiting
- The success rate depends on various factors including network conditions and faucet availability

## 🛡️ Safety & Best Practices

- Never share your `2captcha.txt` or private keys
- Use this bot responsibly and respect the faucet's rate limits
- Consider using proxies for better reliability
- Monitor your 2captcha balance to avoid interruptions

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**VONSSY**

## 🙏 Acknowledgments

- Pharos Atlantic Faucet team
- 2captcha.com for CAPTCHA solving service
- Web3.py community

## 📞 Support

If you encounter any issues or have questions:
1. Check the existing issues on GitHub
2. Create a new issue with detailed information
3. Join our community discussions

---

⭐ If you find this bot helpful, please give it a star!

## Disclaimer

This bot is for educational purposes only. Use it responsibly and at your own risk. The authors are not responsible for any misuse or damage caused by this software.
