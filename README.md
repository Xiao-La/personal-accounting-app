# 🏦 Personal Accounting Web App

A full-featured personal accounting web application built with Flask, featuring bilingual support (English/Chinese), interactive reports, and rapid transaction entry.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v2.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🌟 Features

### 💰 **Transaction Management**
- **Quick Entry System**: Rapid transaction input with keyboard shortcuts (1-7 for categories)
- **CRUD Operations**: Add, edit, delete, and view all transactions
- **Smart Categories**: Predefined categories with easy management
- **Auto-descriptions**: Default descriptions for quick entry

### 📚 **Multi-Book Support**
- **Account Books**: Organize transactions into separate books (Personal, Business, etc.)
- **Book Switching**: Easy switching between different account books
- **Independent Data**: Each book maintains separate transaction records

### 📊 **Advanced Reporting**
- **Interactive Charts**: Plotly.js-powered pie charts with hover effects
- **Spending Analytics**: 
  - Where your money goes (majority expenditure analysis)
  - Spending patterns and behavioral insights
  - Top categories breakdown
  - Statistical analysis (averages, min/max, frequency)
- **Visual Insights**: Professional charts with export capabilities

### 🌍 **Bilingual Support**
- **Language Toggle**: Seamless switching between English and Chinese (中文)
- **Complete Coverage**: All UI elements translated
- **Professional Terminology**: Accurate accounting terms in both languages
- **Session Persistence**: Language preference remembered

### ⚡ **User Experience**
- **Responsive Design**: Bootstrap 5 for mobile and desktop
- **Keyboard Shortcuts**: 
  - 1-7: Quick category selection
  - Tab: Navigate between fields
  - Enter: Submit forms
  - Esc: Clear forms
- **Real-time Preview**: Live preview of transaction data
- **Toast Notifications**: User feedback and validation messages

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/personal-accounting-app.git
   cd personal-accounting-app
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Open your browser**
   Navigate to `http://127.0.0.1:5000`

## 📖 Usage Guide

### Getting Started
1. **Create Your First Book**: Click "Books" → Enter book name → "Add"
2. **Add Categories**: Go to "Categories" to customize your expense categories
3. **Start Adding Transactions**: Use the "Add" page with keyboard shortcuts for rapid entry
4. **View Reports**: Check "Report" for spending analytics and interactive charts
5. **Switch Languages**: Click the globe icon (🌐) to toggle between English/中文

### Keyboard Shortcuts (Add Page)
- **1-7**: Select categories instantly
- **Tab**: Move between amount → description → categories
- **Enter**: Submit transaction or advance to next field
- **Esc**: Clear current form

### Multi-Book Workflow
1. Create separate books for different purposes (Personal, Business, Travel, etc.)
2. Use the book selector in the navbar to switch contexts
3. Each book maintains independent transactions and reports

## 🛠️ Technical Details

### Architecture
- **Backend**: Flask (Python web framework)
- **Database**: SQLite with pandas for data manipulation
- **Frontend**: Bootstrap 5 + JavaScript
- **Charts**: Plotly.js for interactive visualizations
- **Icons**: Font Awesome 6

### Database Schema
- **Books**: Account books (id, name)
- **Categories**: Transaction categories (id, name)
- **Transactions**: Transaction records (id, amount, description, category, date, book_id)

### File Structure
```
accounting-app/
├── main.py                 # Main Flask application
├── languages.py            # Bilingual support (English/中文)
├── templates/              # Jinja2 templates
│   ├── base.html          # Base template with navbar
│   ├── index.html         # Transaction list
│   ├── add.html           # Add transaction (rapid entry)
│   ├── report.html        # Analytics and charts
│   ├── books.html         # Book management
│   ├── categories.html    # Category management
│   └── edit.html          # Edit transactions
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables
- `FLASK_DEBUG`: Set to `True` for development
- `SECRET_KEY`: Change the default secret key for production

### Database
- SQLite database (`accounting.db`) is created automatically
- Backup your database file regularly for data safety

## 🌐 Language Support

The app supports English and Chinese with:
- **Navigation**: 记账, 交易记录, 添加, 报表, 分类, 账本
- **Forms**: 金额, 描述, 分类, 提交, 清空
- **Reports**: 支出报表, 您的资金流向, 支出模式, 统计数据
- **All UI Elements**: Complete translation coverage

## 📊 Sample Reports

The reporting system provides:
- **Majority Expenditure Analysis**: "Food & Dining accounts for $847.32 (43.2%) of total spending"
- **Top 3 Categories**: Combined percentage of highest spending categories
- **Behavioral Insights**: Most frequent category, highest average transaction
- **Statistical Breakdown**: Transaction counts, averages, min/max values

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Bootstrap](https://getbootstrap.com/) - CSS framework
- [Plotly.js](https://plotly.com/javascript/) - Interactive charts
- [Font Awesome](https://fontawesome.com/) - Icons
- [SQLite](https://sqlite.org/) - Database engine

## 📞 Support

If you encounter any issues or have questions:
1. Check the existing issues on GitHub
2. Create a new issue with detailed description
3. Include your Python version and operating system

---

**Made with ❤️ for personal finance management**

*Start taking control of your finances today!* 🚀