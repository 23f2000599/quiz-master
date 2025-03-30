# **Quiz Platform**  

A **web-based quiz management system** built with Flask that enables administrators to create and manage quizzes while allowing students to participate in them.  

### **Project Details**  
- **Developed by:** Smriti S  
- **Roll Number:** 23F2000599  
- **Course:** Modern Application Development - 1 (MAD-1)  
- **Institution:** IIT Madras

---

## **Features**  

### **Admin Features**  
✅ **Subject Management**  
- Create, edit, and delete subjects.

✅ **Chapter Management**  
- Create, edit, and delete chapters under subjects .

✅ **Quiz Management**  
- Create quizzes for specific chapters  
- Set quiz date and duration  
- Edit or delete quizzes  
- View overall performance summary of all users. 

### **Student Features**  
✅ **User Authentication**  
- Secure login system  
- Password reset functionality  

✅ **Quiz Participation**  
- View available quizzes  
- Attempt quizzes within specified time limits  
- Get instant results upon submission  
- Review past quiz attempts and scores  

---

## **Technology Stack**  

### **Backend:**  
- Python 3.x  
- Flask Framework  
- SQLAlchemy (ORM)  
- Flask-Login (Authentication)  

### **Frontend:**  
- HTML5, CSS3, JavaScript  
- Bootstrap 5  

### **Database:**  
- SQLite (Development)  

---

## **Installation Guide**  

(The env, pyache and instance folders have been added to gitignore and hence not added to github)

### **1. Clone the Repository**  
```bash
git clone https://github.com/23f2000599/quiz-master.git
cd quiz-master
```

### **2. Create and Activate a Virtual Environment**  
For **Windows**:  
```bash
python -m venv env
env\Scripts\activate
```
For **Linux/Mac**:  
```bash
python3 -m venv env
source env/bin/activate
```

### **3. Install Dependencies**  
```bash
pip install -r requirements.txt
```


### **4. Run the Application**  
```bash
flask run
```
The application will be available at **`http://127.0.0.1:5000/`**  

---

## **Contributing**  
This project was developed as part of **Modern Application Development - 1 (MAD-1)**. Any contributions or suggestions are welcome! Feel free to fork the repository and submit a pull request.  

---

## **License**  
This project is licensed under the **MIT License**.  

---
