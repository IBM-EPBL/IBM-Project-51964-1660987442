import numpy as np
import os
from flask import Flask, app, request, render_template
import tensorflow 
from keras.models import load_model
from keras.preprocessing import image
from tensorflow.python.ops.gen_array_ops import concat
from keras.applications.inception_v3 import preprocess_input
from cloudant.client import * 
#load model
model = load_model(r"updated-Xception-diabetic-retinopathy .h5")
app = Flask(__name__)
#Authenticate using an IAM API key
client = Cloudant.iam('94bd3ae2-1c46-42ab-9181-3680a03ea6f0-bluemix','HeJzpRSVVgkb6q-2-3UysNRKydgPnbz9CceiiopkRv-d', connect=True)
my_database = client.create_database('my_database')
#create a database using an initialized client
my_database = client.create_database('diabetic_retinopathy')

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/index')
def home():
    return render_template('index.html')
#registration page
@app.route('/Register',methods=['GET'])
def register():
    return render_template('register.html')

@app.route('/afterreg', methods=['POST'])
def afterreg():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    print(name,email,password)

    data = {
        '_id':email,
        'name':name,
        'psw':password,
    }

    print(data)

    query = {'_id': {'$eq': data['_id']}}

    docs = my_database.get_query_result(query)

    print(docs)

    print(len(docs.all()))

    if(len(docs.all())==0):
        url = my_database.create_document(data)
        return render_template('register.html', pred="Registration successfull, Please login using your details")
    else:
        return render_template('register.html', pred="You are already a member, Please login using your details")
#login page
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/afterlogin' , methods=['POST'])
def afterlogin():

    user = request.form.get('email')
    passw = request.form.get('psw')
    print(user,passw)

    query = {'_id': {'$eq': user}}

    docs = my_database.get_query_result(query)
    print(docs)

    print(len(docs.all()))
    if(len(docs.all())==0):
        return render_template('login.html', pred="The username is not found, please Register")
    else:
        if((user==docs[0][0]['_id'] and passw==docs[0][0]['psw'])):
            return render_template('index.html')
        else:
            print('Invalid User')


@app.route('/logout')
def logout():
    return render_template('logout.html')


#prediction
@app.route('/result')
def result():
    return render_template('result.html',pred=None)

@app.route('/prediction', methods=['GET','POST'])
def pred_view():
    if request.method== 'GET':
        return render_template('prediction.html')

    elif request.method == 'POST':
        f = request.files['image']
        basepath = os.path.dirname(__file__) #getting the current pah i.e. where app.py is present
        filepath=os.path.join(basepath,'uploads',f.filename)
        f.save(filepath)

        img = image.load_img(filepath,target_size=(299,299))
        x = image.img_to_array(img)
        x=np.expand_dims(x,axis=0)#used for adding one more dimension
        img_data=preprocess_input(x)
        prediction=np.argmax(model.predict(img_data),axis=1)

        # prediction = model.predict(x)
        print("prediction is", prediction)

        index=['No Diabetic Retinopathy', 'Mild Diabetic Retinopathy', 'Moderate Diabetic Retinopathy', 'Severe Diabetic Retinopathy', 'Proliferative Diabetic Retinopathy']

        res = str(index[prediction[0]])
      
        print(res)

        return render_template('result.html',pred=res)

if __name__ == "__main__":
    app.run()