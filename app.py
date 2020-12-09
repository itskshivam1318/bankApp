from flask import Flask,flash,render_template,request,redirect,session,url_for,g
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Shkh!Tant'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class User:
    def __init__(self,id,username,password,role):
        self.id =id
        self.username = username
        self.password = password
        self.role = role

    # def __repr__(self):
    #     return f'<User:{self.username}>'

users = []
users.append(User(id=1,username="shivam",password="password",role="CAE"))
users.append(User(id=2,username="soham",password="wordpass",role="Cashier"))

class Customer(db.Model):
    ssn = db.Column(db.Integer,nullable=False)
    customer_id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(25),nullable=False)
    address= db.Column(db.String(100),nullable=False)
    age = db.Column(db.Integer,nullable=False)
    accounts = db.relationship('Account',backref='owner')

class Account(db.Model):
    customer_id = db.Column(db.Integer,db.ForeignKey('customer.customer_id'))
    account_id = db.Column(db.Integer,primary_key=True)
    account_type = db.Column(db.String(10),nullable=False)
    balance = db.Column(db.Integer,nullable=False)
    # cr_date
    # cr_last_date
    # duration
class Transaction(db.Model):
    transaction_id = db.Column(db.Integer,primary_key=True)
    customer_id = db.Column(db.Integer,nullable=False)
    account_id = db.Column(db.Integer,nullable=False)
    account_type = db.Column(db.String(10),nullable=False)
    amount = db.Column(db.Integer,nullable=False)
    transaction_type = db.Column(db.String(10),nullable=False)
    transaction_date = db.Column(db.DateTime,default =datetime.utcnow)
    source_account = db.Column(db.Integer)
    target_account = db.Column(db.Integer)
# @app.before_request
# def before_request():
#     g.user = None
#     if 'user_id' in session:
#         user = [x for x in users if x.id == session['user_id']][0]
#         g.user = user

@app.route('/login',methods=['GET','POST'])
def login():
    print(session)
    error = None
    if request.method == 'POST':
        session['user_id']=None
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        user = [x for x in users if x.username == username][0]
        if user and user.password == password:
            # flash('You were sucessfully logged in')
            if user.role == role:
                session['user_id'] = user.id
                session['role'] = user.role
                return redirect(url_for(role))
        error = 'Invalid cerdentials'

    return render_template('login.html',error=error)      

@app.route('/CAEDashboard')
def CAE():
    print(session)
    if session['user_id'] == None:
        return redirect(url_for('login'))
    if session['role'] != 'CAE':
        return redirect(url_for('Cashier'))
    return render_template('CAE_Dashboard.html')

@app.route('/CashierDashboard')
def Cashier():
    print(session)
    if session['user_id'] == None:
        return redirect(url_for('login'))
    if session['role'] != 'Cashier':
        return redirect(url_for('CAE'))
    return render_template('Cashier_Dashboard.html')

@app.route('/logout')
def logout():
    session['user_id'] = None
    session['role'] = None
    return render_template('login.html')

@app.route('/createCustomer',methods=['POST','GET'])
def createCustomer():
    if request.method == "POST":
        ssn = request.form['ssn']
        name = request.form['name']
        address = request.form['address']
        age = request.form['age']
        new_customer = Customer(ssn=ssn,name=name,address=address,age=age)
        print(new_customer)

        try:
            db.session.add(new_customer)
            db.session.commit()
            return redirect('/showCustomer')
        except:
            return 'There was an problem creating the customer.'
    else:
        # customers = Customer.query.order_by(Customer.customer_id).all()
        return render_template('createCustomer.html')

@app.route('/updateCustomer/<int:customer_id>',methods=['POST','GET'])
def updateCustomer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if request.method == 'POST':
        customer.ssn = request.form['ssn']
        customer.name = request.form['name']
        customer.address = request.form['address']
        customer.age = request.form['age']

        try:
            db.session.commit()
            return redirect('/showCustomer')
        except:
            return 'There was an problem in updating the customer'
    else:
        return render_template('updateCustomer.html',customer=customer)    

@app.route('/deleteCustomer/<int:customer_id>')
def deleteCustomer(customer_id):
    Customer_to_delete = Customer.query.get_or_404(customer_id)

    try:
        db.session.delete(Customer_to_delete)
        db.session.commit()
        return redirect('/showCustomer')
    except:
        return 'There was problem deleting the customer.'

@app.route('/showCustomer')
def showCustomer():
    customers = Customer.query.order_by(Customer.customer_id).all()
    return render_template('showCustomer.html',customers=customers)

@app.route('/createAccount',methods=['GET','POST'])
def createAccount():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        account_type = request.form['account_type']
        balance = request.form['balance']
        # cr_date
        # cr_last_date
        # duration
        # customer_obj = Customer.query.filter_by(customer_id=customer_id)
        customer_obj = Customer.query.get_or_404(customer_id)
        new_account = Account(customer_id=customer_obj.customer_id,account_type=account_type,balance=balance)
        print (new_account)

        try:
            db.session.add(new_account)
            db.session.commit()
            return redirect('/CAEDashboard')
        except:
            return 'There was a problem in creating'

    else:
        return render_template('createAccount.html')

@app.route('/deleteAccount/<int:account_id>')
def deleteAccount(account_id):
    account_to_delete = Account.query.get_or_404(account_id)

    try:
        db.session.delete(account_to_delete)
        db.session.commit()
        return redirect('/showAccount')
    except:
        return 'There was a problen deleting the account'

@app.route('/showAccount')
def showAccount():
    accounts = Account.query.order_by(Account.customer_id).all()
    return render_template('showAccount.html',accounts=accounts)

@app.route('/depositMoney',methods=['GET','POST'])
def depositMoney():
    if request.method == 'POST':
        account_id = request.form['account_id']
        amount = request.form['amount']

        account_obj = Account.query.get_or_404(account_id) 
        new_transaction = Transaction(customer_id = account_obj.customer_id,
        account_id = account_id,account_type=account_obj.account_type,
        amount=amount,transaction_type="Credit(deposit)")

        update_balance = int(account_obj.balance) + int(amount)
        account_obj.balance = update_balance

        try:
            db.session.add(new_transaction)
            db.session.commit()
            return redirect('/showTransaction')
        except:
            return 'Transaction failed'
    else:
        return render_template('depositMoney.html')

@app.route('/withdrawMoney',methods=['GET','POST'])
def withdrawMoney():
    if request.method == 'POST':
        account_id = request.form['account_id']
        amount = request.form['amount']

        account_obj = Account.query.get_or_404(account_id) 
        new_transaction = Transaction(customer_id = account_obj.customer_id,
        account_id = account_id,account_type=account_obj.account_type,
        amount=amount,transaction_type="Debit(Withdraw)")

        update_balance = int(account_obj.balance) - int(amount)
        account_obj.balance = update_balance

        try:
            db.session.add(new_transaction)
            db.session.commit()
            return redirect('/showTransaction')
        except:
            return 'Transaction failed'
    else:
        return render_template('withdrawMoney.html')

@app.route('/transferMoney',methods=['GET','POST'])
def transferMoney():
    if request.method == 'POST':
        account_id = request.form['account_id']
        target_id = request.form['target_id']
        amount = request.form['amount']

        account_obj = Account.query.get_or_404(account_id) 
        target_account_obj = Account.query.get_or_404(target_id)

        new_Debit_transaction = Transaction(customer_id = account_obj.customer_id,
        account_id = account_id,account_type=account_obj.account_type,
        amount=amount,transaction_type="Debit(transfer)",source_account=account_id,target_account=target_id)

        new_Credit_transaction = Transaction(customer_id = target_account_obj.customer_id,
        account_id = target_id,account_type=target_account_obj.account_type,
        amount=amount,transaction_type="Credit(transfer)",source_account=account_id,target_account=target_id)

        update_Account_balance = int(account_obj.balance) - int(amount)
        account_obj.balance = update_Account_balance

        target_Account_balance = int(target_account_obj.balance) + int(amount)
        target_account_obj.balance = target_Account_balance

        try:
            db.session.add(new_Debit_transaction)
            db.session.add(new_Credit_transaction)
            db.session.commit()
            return redirect('/showTransaction')
        except:
            return 'Transaction failed'
    else:
        return render_template('transferMoney.html')

@app.route('/showTransaction')
def showTransaction():
    transactions = Transaction.query.order_by(Transaction.transaction_date).all()
    return render_template('showTransaction.html',transactions=transactions)

@app.route('/printStatement',methods=['GET','POST'])
def printStatement():
    pass
    
if __name__ == "__main__":
    app.run(debug=True)

        
