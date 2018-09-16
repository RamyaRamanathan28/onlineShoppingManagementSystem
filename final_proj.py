from flask import Flask, render_template, request, json, session, url_for, redirect, flash
from passlib.hash import sha256_crypt
import time
import datetime
app = Flask(__name__)
import MySQLdb

app.secret_key = 'many random bytes'
app.config['APPLICATION_ROOT'] = True
db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                     passwd=" ",  # your password
                     db="SHOPS")        # name of the data base

f = '%Y-%m-%d %H:%M:%S'

cur=db.cursor()
verif = 0
cur.execute("SELECT MAX(ID) FROM LOGIN")
customerid = cur.fetchone()[0]
if customerid == None:
        customerid = 0
cur.execute("SELECT MAX(PRODID) FROM PRODUCT")
productid = cur.fetchone()[0]
if productid == None:
        productid = 0

cur.execute("SELECT MAX(FID) FROM FEEDBACK")
feedbackid = cur.fetchone()[0]
if feedbackid == None:
        feedbackid = 0
cur.execute("SELECT MAX(REQID) FROM REQUESTS")
requestid = cur.fetchone()[0]
if requestid == None:
        requestid = 0

cur.execute("SELECT MAX(CATID) FROM CATEGORY")
categoryid = cur.fetchone()[0]
if categoryid == None:
        categoryid = 0

cur.execute("SELECT MAX(ORDERID) FROM ORDERS")
orderid = cur.fetchone()[0]
if orderid == None:
        orderid = 0

cur.execute("SELECT MAX(ID) FROM CART")
cartid = cur.fetchone()[0]
if cartid == None:
        cartid = 0

login=0

@app.route("/catalog/<custid>", methods = ['POST', 'GET'])
def catalog(custid):
        custid = int(custid)
        global login
        if login != custid:
                return redirect(url_for("login", error = 'Please login first!'))
        cur = db.cursor()
        catname = None
        if request.method == 'POST' :
                
                if 'buy' in request.form:
                        PID = str(request.form['buy'])
                        qty = int(request.form['qty'])
                        print PID
                        '''
                        cur2.execute("SELECT QUANTITY FROM STOCK WHERE PRODID=%s",(PID,))
                        stock=int(cur2.fetchone()[0])
                        if qty<stock:
                                flash('not enough stock')
                        '''
                        cur.execute("SELECT PRICE FROM PRODUCT WHERE PRODID = %s;", (PID,))
                        u = cur.fetchall()
                        u2 = str(u[0][0])
                        global cartid
                        cur.execute("INSERT INTO CART VALUES (%s, %s, %s, %s)", (cartid+1 ,PID, custid, u2,))
                        #global cartid
                        cartid = cartid + 1
                        db.commit()
                        cur.execute("SELECT CATID FROM CATEGORY WHERE CATEGORY.CATID = PRODUCT.CATID AND PRODUCT.PRODID = %s", (PID,))
                        user = cur.fetchone()
                        catid = user[0]
                        cur.execute("SELECT PNAME, PDESC, PRODID, PRICE, IMG FROM PRODUCT, CATEGORY WHERE PRODUCT.CATID = CATEGORY.CATID AND CATID = %s;", (catid, )) 
                        products = cur.fetchall()
                        cur.execute("SELECT CATNAME FROM CATEGORY WHERE CATID = %s", (catid, ))
                        user = cur.fetchall()
                        catname = user[0][0]
                elif 'id' in request.form:   
                        catname = str(request.form['id'])
                        print catname
                        cur.execute("SELECT PNAME, PDESC, PRODID, PRICE, IMG FROM PRODUCT, CATEGORY WHERE PRODUCT.CATID = CATEGORY.CATID AND CATNAME = %s;", (catname,)) 
                        products = cur.fetchall()
                        cur.execute("SELECT CATNAME, CATID FROM CATEGORY")
                        user = cur.fetchall()
                '''       
                if 'pid' in request.form:
                        PID = str(request.form['pid'])
                        print 'modal', PID
                        cur2.execute("SELECT PNAME, PDESC, PRODID, PRICE, IMG FROM PRODUCT, CATEGORY WHERE PRODUCT.CATID = CATEGORY.CATID AND CATNAME = %s;", (catname,)) 
                        products = cur2.fetchall()
                '''
                
                        
        else:
                cur = db.cursor()
                cur.execute("SELECT CATNAME, CATID FROM CATEGORY")
                user = cur.fetchall()
                catname = user[0][0]
                cur.execute("SELECT PNAME, PDESC, PRODID, PRICE, IMG FROM PRODUCT, CATEGORY WHERE PRODUCT.CATID = CATEGORY.CATID AND CATNAME = %s;", (catname,)) 
                products = cur.fetchall()
                #catname = products[0][6]
        cur = db.cursor()
        if catname == None:
                cur.execute("SELECT CATNAME, CATID FROM CATEGORY")
                user = cur.fetchall()
                catname = user[0][0]
        cur.execute("SELECT CNAME FROM CUSTOMER WHERE CUSTID = %s", (custid, ))
        cname = cur.fetchone()
        cname = cname[0]
        cur.execute("SELECT SUM(QUANTITY) FROM CART WHERE CUSTID = %s", (custid, ))
        number = cur.fetchone()[0]
        if number is None:
                number=0
        return render_template("catalog.html", data = user, data2 = products, name = catname, custid = custid, cname = cname, number=number)

@app.route("/admin/<eid>/payment_history", methods = ['POST', 'GET'])
def PaymentHist(eid):
        
        eid = int(eid)
        global login
        if login != eid:
                #print login, 'not equal', eid
                return redirect(url_for("login", error = 'Please login first!'))
        cur = db.cursor()
        cur.execute("SELECT ORDERID, CNAME, ORDERAMT, DOO FROM ORDERS O, CUSTOMER C WHERE O.CUSTID=C.CUSTID ORDER BY O.DOO");   
        data = cur.fetchall()
        cur.execute("SELECT ENAME FROM EMPLOYEE WHERE EID = %s", (eid, ))
        ename = cur.fetchone()
        ename = ename[0]
        cur.execute("SELECT AUTH FROM LOGIN WHERE ID = %s", (eid, ))
        auth = cur.fetchone()
        auth = auth[0] 
        return render_template('payment_confirmation.html', data=data, ename=ename,eid=eid, a = auth)



@app.route("/cart/<custid>", methods = ['POST', 'GET'])
def cart(custid):
        custid = int(custid)
        global login
        if login != custid:
                return redirect(url_for("login", error = 'Please login first!'))
        cur2 = db.cursor()
        if request.method == 'POST' :
                if 'remove' in request.form:
                        PID = str(request.form['remove'])
                        print PID
                        cur2.execute("SELECT QUANTITY FROM STOCK WHERE PRODID=%s",(PID,))
                        stock=int(cur2.fetchone()[0])
                        print(stock)
                        cur2.execute("SELECT QUANTITY FROM CART WHERE PRODID=%s",(PID,))
                        qty=int(cur2.fetchone()[0])
                        new_stock=stock+qty
                        print(qty)
                        cur2.execute("UPDATE STOCK SET QUANTITY=%s WHERE PRODID=%s",(new_stock,PID,))
                        db.commit()
                        cur2.execute("DELETE FROM CART WHERE PRODID = %s;", (PID,))
                        db.commit()
                if 'qty' in request.form:
                        print 'xxxx'
                        qty = int(request.form['qty'])
                        PID = str(request.form['pid'])
                        print(qty);
                        cur2.execute("SELECT QUANTITY FROM STOCK WHERE PRODID=%s",(PID,))
                        stock=int(cur2.fetchone()[0])
                        cur2.execute("SELECT QUANTITY FROM CART WHERE PRODID = %s;", ( PID,))
                        old_qty=cur2.fetchone()[0]
                        new_stock=stock+old_qty
                        '''
                        cur2.execute("UPDATE STOCK SET QUANTITY=%s WHERE PRODID=%s",(new_stock,PID,))
                        db.commit()
                        '''
                        print stock
                        if qty<=(stock+old_qty):
                            print 'yyyy'
                            quan2=stock-qty+old_qty
                            cur2.execute("UPDATE CART SET QUANTITY =%s WHERE PRODID = %s;", (qty, PID,))
                            db.commit()
                            cur2.execute("UPDATE STOCK SET QUANTITY=%s WHERE PRODID=%s",(quan2,PID,))
                            db.commit()
                        else:
                            flash('Not enough stock!')
        #change customer ID
                        
        cur2.execute("SELECT PNAME, PDESC, PRODUCT.PRICE, CART.PRODID, IMG, CART.QUANTITY FROM PRODUCT, CART WHERE PRODUCT.PRODID = CART.PRODID AND CART.CUSTID = %s ;", (custid,)) 
        cart = cur2.fetchall()
        #change customer ID
        cur2.execute("SELECT SUM(PRICE*QUANTITY) FROM CART WHERE CUSTID = %s", (custid,))
        total = cur2.fetchone()
        total = total[0]
        #print 'total', total
        cur.execute("SELECT CNAME FROM CUSTOMER WHERE CUSTID = %s", (custid, ))
        cname = cur.fetchone()
        cname = cname[0]
        return render_template("cart.html", cart=cart, total = total, custid = custid, cname = cname)


@app.route("/orderHistory/<custid>", methods = ['POST', 'GET'])
def history(custid):
        custid = int(custid)
        global login
        if login != custid:
                return redirect(url_for("login", error = 'Please login first!'))
        cur = db.cursor()
        print 'x'
        if request.method == 'POST' :
                print 'y'
                if 'oid' in request.form:
                        print 'z'
                        OID = str(request.form['oid'])
                        feedback = str(request.form['feedback'])
                        feedback = feedback.replace("'", "\'")
                        global feedbackid
                        cur.execute("INSERT INTO FEEDBACK VALUES (%s, %s, %s)", (feedbackid+1, OID, feedback,))
                        #global feedbackid
                        feedbackid = feedbackid + 1
                        db.commit()
                        flash('Your feedback has been submitted!')
                        '''
                        cur2.execute("SELECT PNAME, PDESC, PRODUCT.PRICE, PRODUCT.PRODID FROM PRODUCT, ORDER_PROD WHERE %s = ORDER_PROD.ORDERID AND ORDER_PROD.PRODID = PRODUCT.PRODID" , (OID,))
                        data = cur2.fetchall()
                        return render_template("view.html", history = data)
                        '''
        cur.execute("SELECT ORDERID FROM ORDERS WHERE CUSTID = %s", (custid,))
        history = cur.fetchall()
        cur.execute("SELECT CNAME FROM CUSTOMER WHERE CUSTID = %s", (custid, ))
        cname = cur.fetchone()
        cname = cname[0]
        #cur2.execute("SELECT PNAME, PDESC, PRODUCT.PRICE, PRODUCT.PRODID FROM ORDERS, PRODUCT, ORDER_PROD WHERE ORDERS.CUSTID = %s AND ORDERS.ORDERID = ORDER_PROD.ORDERID AND ORDER_PROD.PRODID = PRODUCT.PRODID", ('00001',))
        #history = cur2.fetchall()
        return render_template("history.html", history = history, custid = custid, cname = cname)

@app.route("/viewOrder/<custid>/<orderid>", methods = ['POST', 'GET'])
def viewOrder(custid, orderid):
        custid = int(custid)
        orderid = int(orderid)
        global login
        if login != custid:
                return redirect(url_for("login", error = 'Please login first!'))
        cur2 = db.cursor()
        #orderid = request.args.get('orderid')
        cur2.execute("SELECT PNAME, PDESC, PRODUCT.PRICE, PRODUCT.PRODID, IMG, QUANTITY FROM PRODUCT, ORDER_PROD WHERE ORDER_PROD.ORDERID = %s AND ORDER_PROD.PRODID = PRODUCT.PRODID", (orderid,))
        history = cur2.fetchall()
        cur.execute("SELECT CNAME FROM CUSTOMER WHERE CUSTID = %s", (custid, ))
        cname = cur.fetchone()
        cname = cname[0]
        cur2.execute("SELECT ORDERAMT FROM ORDERS CART WHERE ORDERID = %s", (orderid,))
        total = cur2.fetchone()
        total = total[0]
        return render_template("viewCust.html", history = history, custid = custid, cname = cname, total=total)
        
        
'''
               cur.execute("SELECT * FROM PRODUCT WHERE CATID == %s") 
        else :
                cur.execute("SELECT * FROM PRODUCT WHERE CATID == %s")
'''


@app.route("/requests/<custid>", methods = ['POST', 'GET'])
def requests(custid):
        custid = int(custid)
        global login
        if login != custid:
                return redirect(url_for("login", error = 'Please login first!'))
        cur2 = db.cursor()
        if request.method == 'POST' :
                print 'y'
                if 'request' in request.form:
                        print 'x'
                        custID = str(request.form["request"])
                        print custID          
                        prodname = str(request.form["prodname"])
                        proddesc = str(request.form["proddesc"])
                        proddesc = proddesc.replace("'", "\'")
                        prodname = prodname.replace("'", "\'")
                        print prodname, proddesc
                        global requestid
                        cur2.execute("INSERT INTO REQUESTS VALUES (%s, %s, %s, %s, %s)", (requestid + 1, custid, prodname, proddesc, 'PENDING'))
                        #global requestid
                        requestid = requestid + 1
                        db.commit()
                        flash('Your request has been submitted!')
                        
        cur = db.cursor()
        cur.execute("SELECT CATNAME, CATID FROM CATEGORY")
        user = cur.fetchall()
        cur.execute("SELECT * FROM REQUESTS WHERE CUSTID = %s", (custid,))
        requests = cur.fetchall()
        cur.execute("SELECT CNAME FROM CUSTOMER WHERE CUSTID = %s", (custid, ))
        cname = cur.fetchone()
        cname = cname[0]
        return render_template("requests.html", data=user, requests = requests, custid = custid, cname = cname)

@app.route("/address/<custid>", methods = ['POST', 'GET'])
def address(custid):
        custid = int(custid)
        global login
        if login != custid:
                return redirect(url_for("login", error = 'Please login first!'))
        cur = db.cursor()
        if request.method == 'POST' :
                if 'zip' in request.form:
                        zipp = str(request.form['zip'])
                        city = str(request.form['city'])
                        area = str(request.form['area'])
                        street = str(request.form['street'])
                        houseno = str(request.form['house_no'])
                        print area
                        cur.execute("UPDATE CUSTOMER SET CHOUSENO = %s WHERE CUSTID = %s", (houseno, custid,))
                        cur.execute("UPDATE CUSTOMER SET CSTREET = %s WHERE CUSTID = %s", (street, custid,))
                        cur.execute("UPDATE CUSTOMER SET CAREA = %s WHERE CUSTID = %s", (area, custid,))
                        cur.execute("UPDATE CUSTOMER SET CCITY = %s WHERE CUSTID = %s", (city, custid,))
                        cur.execute("UPDATE CUSTOMER SET CZIP = %s WHERE CUSTID = %s", (zipp, custid,))
                        db.commit()
                        return redirect(url_for('pay', custid = custid))
        cur.execute("SELECT CHOUSENO, CSTREET, CAREA, CCITY, CZIP FROM CUSTOMER WHERE CUSTID = %s;", (custid,)) 
        addr = cur.fetchone()
        cur.execute("SELECT CNAME FROM CUSTOMER WHERE CUSTID = %s", (custid, ))
        cname = cur.fetchone()
        cname = cname[0]
        return render_template("address.html", item = addr, custid = custid, cname = cname)


@app.route("/payment/<custid>", methods = ['POST', 'GET'])
def pay(custid):
        custid = int(custid)
        global login
        if login != custid:
                return redirect(url_for("login", error = 'Please login first!'))
        cur = db.cursor()
        print 'x'
        cur.execute("SELECT CNAME FROM CUSTOMER WHERE CUSTID = %s", (custid, ))
        cname = cur.fetchone()
        cname = cname[0]
        if request.method == 'POST' :
                print 'y'
                if 'card_number' in request.form:
                        cardno = str(request.form['card_number'])
                        print cardno
                        cvv = str(request.form['cvv'])
                        print cvv
                        noc = str(request.form['noc'])
                        print noc
                        exp_year = str(request.form['exp_year'])
                        print exp_year
                        exp_month =str(request.form['exp_month'])
                        print 'exp month', exp_month
                        cur.execute("SELECT * FROM PAYMENT WHERE CARDID = %s", (cardno,))
                        data = cur.fetchone()
                        if data:
                                pass
                        else:
                                time.sleep(2)
                                return redirect(url_for('incorrect_payment', custid = custid))
                                
                        if str(data[1])==exp_year and str(data[2])==exp_month and str(data[3])==cvv and str(data[4])==noc:
                                print 'r'
                                global verif
                                verif = custid
                                return redirect(url_for('verif', custid = custid, cardno = cardno, cname = cname))
                        else:
                                flash("The card details you entered are incorrect")
                                time.sleep(2)
                                return redirect(url_for('incorrect_payment', custid = custid))
                                        
        
        return render_template("payment_det.html", custid = custid, cname = cname)

@app.route("/incorrect_payment/<custid>", methods = ['POST', 'GET'])
def incorrect_payment(custid):
        return render_template("payment_incorrect.html", data = custid)

@app.route("/verification/<custid>/<cardno>", methods = ['POST', 'GET'])
def verif(custid, cardno):
        custid = int(custid)
        global login
        if login != custid:
                return redirect(url_for("login", error = 'Please login first!'))
        global verif
        if verif != custid:
                return redirect(url_for("incorrect_payment", custid=custid))
        cur = db.cursor()  
        if request.method == 'POST' :
                print 'x'
                if 'password' in request.form:
                        print 'y'
                        passw = str(request.form['password'])
                        cur.execute("SELECT PASSWORD FROM PAYMENT WHERE CARDID = %s", (cardno,))
                        data = cur.fetchone()
                        print data
                        print passw
                        if sha256_crypt.verify(passw, data[0]):
                                cur.execute("SELECT PRICE, QUANTITY FROM CART WHERE CUSTID = %s", (custid,))
                                vals = cur.fetchall()
                                cost = 0
                                for x in vals:
                                        cost = cost + x[0]*x[1]
                                now = datetime.datetime.now()
                                timestamp = now.strftime(f)
                                print 'okay'
                                global orderid  
                                cur.execute("INSERT INTO ORDERS VALUES(%s, %s, %s, %s)", (orderid + 1, custid, cost, timestamp))
                                #global orderid  
                                orderid = orderid + 1
                                db.commit()
                                cur.execute("SELECT PRODID, QUANTITY FROM CART WHERE CUSTID = %s", (custid,))
                                data = cur.fetchall()
                                
                                for item in data:
                                        #global orderid
                                        cur.execute("INSERT INTO ORDER_PROD VALUES(%s,%s, %s)", (orderid, item[0],item[1]))
                                        db.commit()
                                cur.execute("DELETE FROM CART WHERE CUSTID = %s", (custid,))
                                db.commit()
                                return redirect(url_for('viewOrder', custid = custid, orderid = orderid))
                        else:
                                return redirect(url_for('incorrect_payment', custid = custid))

        cur.execute("SELECT CNAME FROM CUSTOMER WHERE CUSTID = %s", (custid, ))
        cname = cur.fetchone()
        cname = cname[0]
        return render_template("verification.html", item = cardno, custid = custid, cname = cname)



@app.route("/admin/<eid>/modify-category", methods = ['POST', 'GET'])
def Category(eid):
        eid = int(eid)
        global login
        if login != eid:
                return redirect(url_for("login", error = 'Please login first!'))
        cur = db.cursor()
        cur.execute("SELECT AUTH FROM LOGIN, EMPLOYEE WHERE EMPLOYEE.EID = %s && EMPLOYEE.EUSERNAME=LOGIN.UNAME", (eid,))
        a=cur.fetchone()
        a=a[0] 
        if request.method== 'POST':
                print 'x'
                if 'cat_id2' in request.form:
                        print 'y'
                        cat_id2=str(request.form["cat_id2"])
                        cat_name2= str(request.form["cat_name2"])
                        cat_desc2= str(request.form["cat_desc2"])
                        cat_name2 = cat_name2.replace("'", "\'")
                        cat_desc2 = cat_desc2.replace("'", "\'")
                        cur2 = db.cursor()
                        cur2.execute("Update CATEGORY set CATNAME=%s, CATDESC=%s where CATID=%s;", ( cat_name2, cat_desc2, cat_id2,))
                        db.commit()
                        flash('Updated successfully.')
                elif 'cat_id3' in request.form:
                        cat_id3=str(request.form["cat_id3"])
                        print(cat_id3)
                        cur2 = db.cursor()
                        cur2.execute("DELETE FROM CATEGORY WHERE CATID=%s", (cat_id3,))
                        db.commit()
                        flash('Deleted successfully.')
                elif 'cat_name' in request.form:
                        #cat_id2= str(request.form["cat_id"])
                        cat_name2= str(request.form["cat_name"])
                        cat_name2 = cat_name2.replace("'", "\'")
                        cat_desc2= str(request.form["cat_desc"])
                        cat_desc2 = cat_desc2.replace("'", "\'")
                        cur2 = db.cursor()
                        global categoryid
                        cur2.execute("INSERT INTO CATEGORY(CATID, CATNAME, CATDESC) VALUES(%s, %s, %s)", (categoryid + 1, cat_name2, cat_desc2,))
                        #global categoryid
                        categoryid = categoryid + 1
                        db.commit()
                        flash('Category added.')
        cur = db.cursor()
        cur.execute("SELECT * FROM CATEGORY")
        data = cur.fetchall()
        cur.execute("SELECT ENAME FROM EMPLOYEE WHERE EID = %s", (eid, ))
        ename = cur.fetchone()
        ename = ename[0]
        cur.execute("SELECT AUTH FROM LOGIN WHERE ID = %s", (eid, ))
        auth = cur.fetchone()
        auth = auth[0] 
        return render_template('template2.html', a=a, data=data, eid = eid, ename = ename, auth = auth)

@app.route("/admin/<eid>/requests", methods = ['POST', 'GET'])
def Requests(eid):
        message=" "
        
        eid = int(eid)
        global login
        if login != eid:
                print login, 'not equal', eid
                return redirect(url_for("login", error = 'Please login first!'))
        cur = db.cursor()
        cur.execute("SELECT AUTH FROM LOGIN, EMPLOYEE WHERE EMPLOYEE.EID = %s && EMPLOYEE.EUSERNAME=LOGIN.UNAME", (eid,))
        a=cur.fetchone()
        a=a[0] 
        if request.method== 'POST':
                print 'x'
                if 'prodname' in request.form:
                        print 'y'
                        #prodid=str(request.form["prodid"])
                        prodname=str(request.form["prodname"])
                        prodname = prodname.replace("'", "\\'")
                        proddesc=str(request.form["proddesc"])
                        proddesc = proddesc.replace("'", "\'")
                        catid=str(request.form["categ"])
                        price=str(request.form["price"])
                        img=str(request.form["img"])
                        stock=str(request.form["stock"])
                        print(catid)
                        cur = db.cursor()
                        global productid
                        cur.execute("INSERT INTO PRODUCT VALUES( %s, %s, %s,%s, %s, %s)", (productid + 1, prodname,proddesc,price, catid, img))
                        db.commit()
                        global productid
                        cur.execute("INSERT INTO STOCK VALUES( %s, %s, %s)", (productid + 1, productid + 1, stock))
                        global productid
                        productid = productid + 1 
                        db.commit()
                        rid=str(request.form["rid"])
                        print(rid)
                        cur.execute("Update REQUESTS set STATUS=%s where REQID=%s;", ( 'COMPLETE', rid))
                        db.commit()
                        message="Product added successfully"
                if 'pid' in request.form:
                        pid=str(request.form["pid"])
                        cur.execute("SELECT PRODID FROM PRODUCT WHERE PRODID = %s", (pid,)) 
                        piddata=cur.fetchone()[0]
                        print piddata
                        if piddata:
                                
                                rid=str(request.form["rid2"])
                                print(rid)
                                cur.execute("Update REQUESTS set STATUS=%s where REQID=%s;", ( 'COMPLETE', rid))
                                db.commit()
                                message="Request completed"
                        else:
                                message ="Request not completed as product does not exist."
         
                        
        cur.execute("SELECT REQID, PRODNAME, PRODDESC FROM REQUESTS where STATUS=%s", ('PENDING',))
        data = cur.fetchall()
        cur.execute("SELECT REQID, PRODNAME, PRODDESC FROM REQUESTS where STATUS=%s", ('COMPLETE',))
        data2 = cur.fetchall()
        cur.execute("SELECT ENAME FROM EMPLOYEE WHERE EID = %s", (eid, ))
        ename = cur.fetchone()
        ename = ename[0]
        cur.execute("SELECT AUTH FROM LOGIN WHERE ID = %s", (eid, ))
        auth = cur.fetchone()
        auth = auth[0]
        cur.execute("SELECT CATID, CATNAME FROM CATEGORY");   
        categ = cur.fetchall()
        return render_template('requestsAdmin.html',a=a, data=data, data2=data2, eid = eid, ename = ename, auth = auth, message=message, categ=categ)

@app.route("/admin/<eid>/feedback", methods = ['POST', 'GET'])
def Feedback(eid):
        eid = int(eid)
        global login
        if login != eid:
                return redirect(url_for("login", error = 'Please login first!'))
        cur = db.cursor()
        cur.execute("SELECT AUTH FROM LOGIN, EMPLOYEE WHERE EMPLOYEE.EID = %s && EMPLOYEE.EUSERNAME=LOGIN.UNAME", (eid,))
        a=cur.fetchone()
        a=a[0] 
        cur.execute("SELECT * FROM FEEDBACK");
        data = cur.fetchall()
        cur.execute("SELECT ENAME FROM EMPLOYEE WHERE EID = %s", (eid, ))
        ename = cur.fetchone()
        ename = ename[0]
        cur.execute("SELECT AUTH FROM LOGIN WHERE ID = %s", (eid, ))
        auth = cur.fetchone()
        auth = auth[0]
        return render_template('feedback.html', a=a,data=data, eid = eid, ename = ename, auth = auth)

@app.route("/AviewOrder/<eid>/<orderid>", methods = ['POST', 'GET'])
def AviewOrder(eid, orderid):
        eid = int(eid)
        orderid = int(orderid)
        global login
        if login != eid:
                return redirect(url_for("login", error = 'Please login first!'))
        cur = db.cursor()
        cur.execute("SELECT AUTH FROM LOGIN, EMPLOYEE WHERE EMPLOYEE.EID = %s && EMPLOYEE.EUSERNAME=LOGIN.UNAME", (eid,))
        a=cur.fetchone()
        a=a[0] 
        cur2 = db.cursor()
        #orderid = request.args.get('orderid')
        cur2.execute("SELECT PNAME, PDESC, PRODUCT.PRICE, PRODUCT.PRODID, IMG, QUANTITY FROM PRODUCT, ORDER_PROD WHERE ORDER_PROD.ORDERID = %s AND ORDER_PROD.PRODID = PRODUCT.PRODID", (orderid,))
        history = cur2.fetchall()
        cur.execute("SELECT ENAME FROM EMPLOYEE WHERE EID = %s", (eid, ))
        ename = cur.fetchone()
        ename = ename[0]
        cur.execute("SELECT AUTH FROM LOGIN WHERE ID = %s", (eid, ))
        auth = cur.fetchone()
        auth = auth[0]
        cur2.execute("SELECT ORDERAMT FROM ORDERS CART WHERE ORDERID = %s", (orderid,))
        total = cur2.fetchone()
        total = total[0]
        return render_template("view.html", a=a,history = history, eid = eid, ename = ename, auth = auth, total=total)


@app.route("/viewProd/<custid>/<prodid>", methods = ['POST', 'GET'])
def viewProd(custid, prodid):
        custid = int(custid)
        prodid = int(prodid)
        global login
        if login != custid:
                return redirect(url_for("login", error = 'Please login first!'))
        cur = db.cursor()
        cur.execute("SELECT L.AUTH FROM LOGIN L, CUSTOMER C WHERE C.CUSERNAME=L.UNAME && C.CUSTID=%s UNION SELECT L.AUTH FROM LOGIN L, EMPLOYEE E WHERE E.EUSERNAME=L.UNAME && E.EID=%s;", (custid,custid,))
        a=cur.fetchone()
        a=a[0] 
        cur2 = db.cursor()
        #orderid = request.args.get('orderid')
        if request.method == 'POST':
                if 'qty' in request.form:
                        PID = str(request.form['prodid'])
                        qty = int(request.form['qty'])
                        price = str(request.form['price'])
                        print PID
                        #change the cust ID thing
                        cur2.execute("SELECT PRODID FROM CART WHERE PRODID=%s",(PID,))
                        test=cur2.fetchone()
                        cur2.execute("SELECT QUANTITY FROM STOCK WHERE PRODID=%s",(PID,))
                        stock=int(cur2.fetchone()[0])
                        if test:
                            cur2.execute("SELECT QUANTITY FROM CART WHERE PRODID=%s",(PID,))
                            quan=cur2.fetchone()[0]
                            quan=quan+qty
                            quan2=stock-qty
                            print quan,stock
                            if qty<=stock:
                                cur2.execute("UPDATE CART SET QUANTITY=%s WHERE PRODID=%s",(quan,PID,))
                                db.commit()
                                cur2.execute("UPDATE STOCK SET QUANTITY=%s WHERE PRODID=%s",(quan2,PID,))
                                db.commit()
                                flash('Added to cart!')
                                #return redirect(url_for("viewProd", prodid = prodid, custid = custid))     
                            else:
                                    flash('Not enough stock!')
                        else:
                            if qty<=stock:
                                quan2=stock-qty
                                cur2.execute("INSERT INTO CART VALUES (%s, %s, %s, %s, %s)", (cartid+1 ,PID, custid, price, qty))
                                db.commit()
                                cur2.execute("UPDATE STOCK SET QUANTITY=%s WHERE PRODID=%s",(quan2,PID,))
                                
                                global cartid
                                cartid = cartid + 1
                                db.commit()
                                flash('Added to cart!')
                                #return redirect(url_for("viewProd", prodid = prodid, custid = custid))
                            else:
                                flash('not enough stock')
                        
        cur2.execute("SELECT PNAME, PDESC, PRODUCT.PRICE, PRODUCT.PRODID, IMG, QUANTITY FROM PRODUCT, STOCK WHERE PRODUCT.PRODID = STOCK.PRODID AND PRODUCT.PRODID = %s", (prodid,))
        history2 = cur2.fetchall()
        '''
        if history2[0][5]>10:
                history= (history2[0][0], history2[0][1], history2[0][2], history2[0][3], history2[0][4])
        else:
        '''
        history = history2[0]
        cur.execute("SELECT CATNAME, CATID FROM CATEGORY")
        data = cur.fetchall()
        cur.execute("SELECT CNAME FROM CUSTOMER WHERE CUSTID = %s", (custid, ))
        cname = cur.fetchone()
        cname = cname[0]
        cur.execute("SELECT SUM(QUANTITY) FROM CART WHERE CUSTID = %s", (custid, ))
        number = cur.fetchone()[0]
        if number is None:
                number=0
        return render_template("viewProduct.html", data = data, item = history, custid = custid, cname = cname, a = a, number=number)
        
        

@app.route("/admin/<eid>/modify-products", methods = ['POST', 'GET'])
def ModifyProduct(eid):
        global login
        eid = int(eid)
        
        if login != eid:
                return redirect(url_for("login", error = 'Please login first!'))
        
        cur = db.cursor()
        cur.execute("SELECT AUTH FROM LOGIN, EMPLOYEE WHERE EMPLOYEE.EID = %s && EMPLOYEE.EUSERNAME=LOGIN.UNAME", (eid,))
        a=cur.fetchone()
        a=a[0] 
        
        if request.method== 'POST':
                print 'x'
                if 'pid2' in request.form:
                        print 'y'
                        pid=str(request.form["pid2"])
                        prodname= str(request.form["prodname2"])
                        
                        categ= str(request.form["categ2"])
                        price=str(request.form["price2"])
                        img= str(request.form["img2"])
                        proddesc=str(request.form["proddesc2"])
                        stock=str(request.form["stock"])
                        proddesc = proddesc.replace("'", "\'")
                        prodname = prodname.replace("'", "\'")
                        print pid, prodname,categ,price,img
                        cur2 = db.cursor()
                        cur2.execute("UPDATE PRODUCT SET PNAME=%s,PDESC=%s,PRICE=%s,IMG=%s, CATID=%s WHERE PRODID=%s;", (prodname,proddesc,price,img,categ,pid,))
                        db.commit()
                        cur2.execute("UPDATE STOCK SET QUANTITY=%s WHERE PRODID=%s;", (stock,pid,))
                        db.commit()
                        flash('Database updated successfully.')
                        
                elif 'pid' in request.form:
                        pid=str(request.form["pid"])
                        cur2 = db.cursor()
                        cur2.execute("DELETE FROM PRODUCT WHERE PRODID=%s", (pid,))
                        db.commit()
                        flash('Product deleted successfully.')
                
                if 'prodname' in request.form:
                        print 'y'
                        #prodid=str(request.form["prodid"])
                        prodname=str(request.form["prodname"])
                        prodname = prodname.replace("'", "\\'")
                        proddesc=str(request.form["proddesc"])
                        proddesc = proddesc.replace("'", "\'")
                        catid=str(request.form["categ"])
                        price=str(request.form["price"])
                        img=str(request.form["img"])
                        stock=str(request.form["stock"])
                        print(catid)
                        cur = db.cursor()
                        global productid
                        cur.execute("INSERT INTO PRODUCT VALUES( %s, %s, %s,%s, %s, %s)", (productid + 1, prodname,proddesc,price, catid, img))
                        db.commit()
                        cur.execute("INSERT INTO STOCK VALUES( %s, %s, %s)", (productid + 1, productid + 1, stock))
                        
                        productid = productid + 1 
                        db.commit()
                        flash('Product added successfully.')
        
        cur.execute("SELECT CATID, CATNAME FROM CATEGORY");   
        data = cur.fetchall()
        cur.execute("SELECT PNAME, PDESC,PRICE,P.PRODID, IMG, S.QUANTITY FROM PRODUCT P, STOCK S WHERE P.PRODID=S.PRODID;")
        data2 = cur.fetchall()
        cur.execute("SELECT ENAME FROM EMPLOYEE WHERE EID = %s", (eid, ))
        ename = cur.fetchone()
        ename = ename[0]
        cur.execute("SELECT AUTH FROM LOGIN WHERE ID = %s", (eid, ))
        auth = cur.fetchone()
        auth = auth[0]
        return render_template('products.html', data=data, data2 = data2, eid = eid, a = a , ename = ename, auth = auth)
        

             
@app.route("/signUp/<error>", methods = ['POST', 'GET'])
def signUp(error):
        if request.method=='POST':
                if 'user' in request.form:
                        print "x"
                        username= str(request.form["user"])
                        print 'username', username
                        name= str(request.form["name"])
                        phone= str(request.form["phone"])
                        altphone= str(request.form["altphone"])
                        passw= str(request.form["password"])
                        password = sha256_crypt.encrypt(passw)
                        email= str(request.form["email"])
                        zipp = str(request.form['zip'])
                        city = str(request.form['city'])
                        area = str(request.form['area'])
                        street = str(request.form['street'])
                        houseno = str(request.form['house_no'])
                        cur = db.cursor()
                        cur.execute("SELECT UNAME FROM LOGIN WHERE UNAME = %s", (username,))
                        test = cur.fetchone()
                        print 'test', test
                        if test:
                                print 'REPEAT'
                                return redirect(url_for("signUp", error = 'Someone\'s already using that username, please choose another one.'))
                        cur = db.cursor()
                        global customerid
                        print customerid
                        cur.execute("INSERT INTO CUSTOMER(CUSTID, CNAME, CUSERNAME, CEMAIL, CHOUSENO, CSTREET, CAREA, CCITY, CZIP) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)", (customerid + 1,name, username, email,houseno, street, area, city, zipp))
                        db.commit()
                        customerid = customerid + 1
                        print 'a'
                        cur.execute("INSERT INTO LOGIN(ID, UNAME, PASS, AUTH) VALUES(%s, %s, %s, %s)", (customerid, username, password, 'C'))
                        db.commit()
                        cur.execute('INSERT INTO PHONE(UID, PHONENO) VALUES (%s, %s)', (customerid, phone,))
                        db.commit()
                        if(altphone):
                                print 'altphone', altphone
                                cur.execute('INSERT INTO PHONE(UID, PHONENO) VALUES (%s, %s)', (customerid, altphone,))
                                db.commit()   
                        print 'b'
                        return redirect(url_for("login", error = "You've been signed up successfully!"))
        return render_template("register.html", error = error)

@app.route("/signin/<error>",  methods = ['POST', 'GET'])
def login(error):
        print 'y'
        if request.method== 'POST':
                print 'x'
                if 'user' in request.form:
                        username= str(request.form["user"])
                        password= str(request.form["password"])
                        print username
                        print password
                        cur = db.cursor()
                        cur.execute("SELECT UNAME FROM LOGIN WHERE UNAME='"+username+"'")
                        user=cur.fetchone()
                        if user == None:
                                return redirect(url_for("signUp", error = 'We can\'t find that username in our records, please check what you\'ve entered.'))
                        else:
                                cur.execute("SELECT PASS FROM LOGIN WHERE UNAME='"+username+"'")
                                passw = cur.fetchone()
                                print str(passw[0])
                                print password
                                if sha256_crypt.verify(password, str(passw[0])):
                                        print 'They are equal'
                                        cur.execute("SELECT AUTH FROM LOGIN WHERE UNAME='"+username+"'")
                                        auth = cur.fetchone()
                                        if auth[0]=='E' or auth[0]=='A':
                                                cur.execute("SELECT EID FROM EMPLOYEE WHERE EUSERNAME LIKE %s", (username,))
                                                data = cur.fetchone()
                                                global login
                                                login=int(data[0])
                                                print 'login', type(login)
                                                return redirect(url_for("Requests", eid = login))
                                                
                                        else:
                                                cur.execute("SELECT CUSTID FROM CUSTOMER WHERE CUSERNAME LIKE %s", (username,))
                                                data = cur.fetchone()
                                                #global login
                                                login=int(data[0])
                                                return redirect(url_for("catalog", custid = login))
                                        
                                else :
                                        return redirect(url_for("login", error = 'Incorrect password, please try again!'))
        return render_template("signin.html", error = error)

@app.route("/search/<custid>", methods = ['POST', 'GET'])
def search(custid):
        custid = int(custid)
        global login
        if login != custid:
                return redirect(url_for("login", error = 'Please login first!'))
        cur = db.cursor()
        cur.execute("SELECT CNAME FROM CUSTOMER WHERE CUSTID = %s", (custid, ))
        cname = cur.fetchone()
        cname = cname[0] 
        if request.method== 'POST':
                print 'x'
                if 'search' in request.form:
                        print 'y'
                        cur.execute("SELECT CATNAME, CATID FROM CATEGORY");
                        data = cur.fetchall()
                        search=str(request.form["search"])
                        search1 = '%' + search + '%'
                        search2 = '%' + search.lower() + '%'
                        search3 = '%' + search.upper() + '%'
                        search4 = '%' + search.title() + '%'
                        search5 = '%' + search.capitalize() + '%'
                        cur.execute("SELECT PNAME,PDESC, PRODID, PRICE, IMG FROM PRODUCT WHERE PNAME LIKE %s OR PDESC LIKE %s OR PNAME LIKE %s OR PDESC LIKE %s OR PNAME LIKE %s OR PDESC LIKE %s OR PNAME LIKE %s OR PDESC LIKE %s OR PNAME LIKE %s OR PDESC LIKE %s;", (search1,search1,search2,search2,search3,search3,search4,search4,search5,search5,))
                        data2=cur.fetchall()
                        return render_template('search.html', data=data, data2=data2, custid = custid, cname = cname)
        cur.execute("SELECT CATNAME, CATID FROM CATEGORY");
        data = cur.fetchall()
        cur.execute("SELECT PNAME,PDESC,PRODID, PRICE, IMG FROM PRODUCT")
        data2=cur.fetchall()
        cur.execute("SELECT CNAME FROM CUSTOMER WHERE CUSTID = %s", (custid, ))
        cname = cur.fetchone()
        cname = cname[0] 
        return render_template('search.html', data=data, data2=data2, custid = custid, cname = cname)
             
@app.route("/admin/<eid>/addAdmin", methods = ['POST', 'GET'])
def addAdmin(eid):
        eid = int(eid)
        global login
        if login != eid:
                return redirect(url_for("login", error = 'Please login first!'))
        cur = db.cursor()
        if request.method=='POST':
                if 'user' in request.form:
                        print "x"
                        username= str(request.form["user"])
                        name= str(request.form["name"])
                        phone= str(request.form["phone"])
                        altphone= str(request.form["altphone"])
                        password= str(request.form["password"])
                        password = sha256_crypt.encrypt(password)
                        email= str(request.form["email"])
                        a=str(request.form["authorization"])
                        cur = db.cursor()
                        cur.execute("SELECT UNAME FROM LOGIN WHERE UNAME = %s", (username,))
                        test = cur.fetchone()
                        if test:
                                print 'test'
                                cur.execute("SELECT ENAME FROM EMPLOYEE WHERE EID = %s", (eid, ))
                                ename = cur.fetchone()
                                ename = ename[0]
                                flash('Username in use')
                                #return redirect(url_for("addAdmin", eid = eid, ename = ename))
                        else:
                                cur = db.cursor()
                                global customerid
                                cur.execute("INSERT INTO EMPLOYEE(EID, ENAME, EUSERNAME, EEMAIL) VALUES(%s, %s, %s, %s)", (customerid + 1,name, username, email,))
                                db.commit()
                                customerid = customerid + 1
                                cur.execute("INSERT INTO LOGIN(ID, UNAME, PASS, AUTH) VALUES(%s, %s, %s, %s)", (customerid, username, password, a))
                                db.commit()
                                cur.execute('INSERT INTO PHONE(UID, PHONENO) VALUES (%s, %s)', (customerid, phone,))
                                db.commit()
                                if(altphone):
                                        print 'altphone', altphone
                                        cur.execute('INSERT INTO PHONE(UID, PHONENO) VALUES (%s, %s)', (customerid, altphone,))
                                        db.commit()   
                                cur.execute("SELECT ENAME FROM EMPLOYEE WHERE EID = %s", (eid, ))
                                ename = cur.fetchone()
                                ename = ename[0] 
                                flash('Admin added successfully!')
                                #return redirect(url_for("addAdmin", eid = eid, ename = ename))
        cur.execute("SELECT ENAME FROM EMPLOYEE WHERE EID = %s", (eid, ))
        ename = cur.fetchone()
        ename = ename[0] 
        return render_template("admin_register.html", eid = eid, ename = ename)


@app.route("/accountDetails/<custid>", methods = ["POST", "GET"])
def accDet(custid):
        custid = int(custid)
        global login
        if login != custid:
                return redirect(url_for("login", error = 'Please login first!'))
        cur = db.cursor()
        cur.execute("SELECT AUTH FROM LOGIN WHERE ID = %s", (custid,))
        auth = cur.fetchone();
        auth = auth[0]
        print auth
        if auth == 'C':
                cur.execute("SELECT CNAME, CEMAIL, CUSERNAME, CHOUSENO, CSTREET, CAREA, CCITY, CZIP FROM CUSTOMER WHERE CUSTID = %s", (custid,))
                cust = cur.fetchone()
                print cust
                auth = 'Customer'
                print cust
                return render_template("accountDetailsCust.html", custid = custid, auth = auth,a = auth[0], cust = cust)
        elif auth == 'E' :
                cur.execute("SELECT ENAME, EEMAIL, EUSERNAME FROM EMPLOYEE WHERE EID = %s", (custid,))
                cust = cur.fetchone();
                auth = 'Employee'
                return render_template("accountDetails.html", eid = custid, auth = auth,a = auth[0], cust = cust)
        else : 
                cur.execute("SELECT ENAME, EEMAIL, EUSERNAME FROM EMPLOYEE WHERE EID = %s", (custid,))
                cust = cur.fetchone();
                auth = 'Administrator'
                return render_template("accountDetails.html", eid = custid, auth = auth,a = auth[0], cust = cust)
        
@app.route("/logout/<custid>", methods = ["POST", "GET"])
def logout(custid):
        print {'entered logout'}
        custid = int(custid)
        global login
        if login != custid:
                return redirect(url_for("login", error = 'Please login first!'))
        else :
                login = 0
                return redirect(url_for("login", error = 'You have been successfully logged out!'))

@app.route("/change_password/<custid>", methods = ['POST', 'GET'])
def changePass(custid):
        custid = int(custid)
        global login
        if login != custid:
                return redirect(url_for("login", error = 'Please login first!'))
        cur = db.cursor()
        if request.method=='POST':
                if 'password' in request.form:
                        print "x"
                        old= str(request.form["password"])
                        print 'old', old
                        new= str(request.form["new_password"])
                        if old==new:
                                flash('Please do not reuse the same password!')
                        else:
                                password = sha256_crypt.encrypt(new)
                                cur.execute("SELECT PASS,UNAME, AUTH FROM LOGIN WHERE ID= %s", (custid,))
                                data=cur.fetchone()
                                test = data[0]
                                uname=data[1]
                                print test,'test'
                                print uname, 'uname'
                                if sha256_crypt.verify(old, test):
                                    cur.execute("UPDATE LOGIN SET PASS=%s WHERE UNAME = %s", (password,uname,))
                                    db.commit()
                                    print uname, new, password
                                    flash("Password successfully changed")
                                else:
                                    flash("Incorrect password");
                                
        cur.execute("SELECT AUTH FROM LOGIN WHERE ID= %s", (custid,))
        data=cur.fetchone()
        print data
        auth = data[0]
        if auth=='C':
                cur.execute("SELECT CNAME FROM CUSTOMER WHERE CUSTID = %s", (custid, ))
                cname = cur.fetchone()
                cname = cname[0] 
                return render_template("change_password.html", custid=custid, cname = cname)
        else :
                cur.execute("SELECT ENAME FROM EMPLOYEE WHERE EID = %s", (custid, ))
                ename = cur.fetchone()
                print ename
                ename = ename[0]
                cur.execute("SELECT AUTH FROM LOGIN WHERE ID = %s", (custid, ))
                auth = cur.fetchone()
                auth = auth[0]
                return render_template("change_passwordAdmin.html", eid=custid, ename = ename, auth = auth, a = auth)                


@app.route("/", methods = ["POST", "GET"])
def index():
        return redirect(url_for("login", error = 'None'))
                         
if __name__ == "__main__":
    app.run(debug = True)
