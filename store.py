from bottle import route, run, template, static_file, get, post, delete, request
from sys import argv
import json
import pymysql

connection = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             db='store',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor
                             )


@get("/admin")
def admin_portal():
    return template("pages/admin.html")


@get("/")
def index():
    return template("index.html")


@get("/category", method="POST")
def category():  # this is supposed to create the category it is being fed.

    name = request.POST.get('name')

    msg = None
    cat_id = None
    code = None
    status = None

    succ_status = "SUCCESS"
    err_status = 'ERROR'

    err_msg1 = "Category already exists"
    err_msg2 = "Name parameter is missing"
    err_msg3 = "Internal error"

    code201 = "201 category created successfully"
    code200 = "200  category already exists "
    code400 = "400  bad request"
    code500 = "500  internal error"

    if not name:
        code = code400
        status = err_status
        msg = err_msg2
        return {"STATUS": status, "MSG": msg, "CAT_ID": cat_id, "CODE": code}

    else:

        try:
            with connection.cursor() as cursor:
                sql = 'INSERT INTO category (name) VALUES("{}")'.format(name)
                cursor.execute(sql)
                connection.commit()
                # result = cursor.fetchall()

        except Exception as e:
            if 1062 in e:
                code = code201
                status = err_status
                msg = err_msg1
                return {"STATUS": status, "MSG": msg, "CAT_ID": cat_id, "CODE": code}
            else:
                code = code500
                status = err_status
                msg = err_msg3
                return {"STATUS": status, "MSG": msg, "CAT_ID": cat_id, "CODE": code}

    code = code200
    status = succ_status
    cat_id = cursor.lastrowid

    return {"STATUS": status, "MSG": msg, "CAT_ID": cat_id, "CODE": code}


@get('/categories')
def categories():
    status = None
    msg = None
    categories = None
    code = None

    try:
        with connection.cursor() as cursor:
            sql = 'SELECT id,name FROM category'
            cursor.execute(sql)
            result = cursor.fetchall()
            status = "SUCCESS"
            categories = result
            code = "200 - success"

    except Exception as e:
        if e:
            status = "ERROR"
            msg = "Internal Error"
            code = "500 - internal error"

    return {"STATUS": status, "MSG": msg, "CATEGORIES": categories, "CODE": code}

@delete('/category/<cat_ID>')
def del_category(cat_ID):
    status = None
    msg = None
    code = None

    try:
        with connection.cursor() as cursor:
            sql = 'DELETE FROM category where id={}'.format(cat_ID)
            category = cursor.execute(sql)
            connection.commit()

    except Exception as e:
        if e:
            status = "ERROR"
            msg = "Internal Error"
            code = "500 - internal error"

    if category != 0:
        status = "SUCCESS"
        code = "201 - success"

    if category == 0:
        status = "ERROR"
        code = '404 - category not found'
        msg = 'category not found'

    return {"STATUS":status, "MSG":msg,  "CODE":code}


@post('/product') #add or edit a product
def add_product():
    product = request.forms

    status = None
    msg = None
    product_id = None
    code = None


    filled_in_all = False


    if product["category"] and product["title"] and product["desc"] and product["price"] and product["img_url"]:
        filled_in_all = True

    if not filled_in_all:
        status = "ERROR"
        msg = "missing parameters"
        code = "400 - bad request"
        return {"STATUS":status, "MSG":msg, "PRODUCT_ID":product_id, "CODE":code}


    if product["id"]:
        pid = product["id"]
    else:
        pid = None

    if product["favorite"]:
        favorite = 1
    else:
        favorite = 0

    cat_id,title,description,price,img = product['category'],product['title'],product['desc'],product['price'],product['img_url']

    if pid:

        try:
            with connection.cursor() as cursor:
                sql = 'UPDATE product SET title="{}", product_desc = "{}", price = {},img_url="{}",id={},favorite={} WHERE product_ID={}'.format(
                title,description,price,img,cat_id,favorite,pid)
                category = cursor.execute(sql)
                connection.commit()

                if category == 0:
                    status = "ERROR"
                    msg = "category not found"
                    code = "404"
                else:
                    status = "SUCCESS"
                    code = 201
                    product_id = pid

        except Exception as e:
            if e:
                status = "ERROR"
                msg = "Internal Error"
                code = "500 - internal error"
                print e

    else:
        try:
            with connection.cursor() as cursor:
                sql = 'INSERT INTO product (title,product_desc,price,img_url,id,favorite) VALUES("{0}","{1}",{2},"{3}",{4},{5})'.format(
                title,description,price,img,cat_id,favorite)
                cursor.execute(sql)
                connection.commit()

        except Exception as e:
            if e:
                status = "ERROR"
                msg = "Internal Error"
                code = "500 - internal error"
                print e

    return {"STATUS":status, "MSG":msg, "PRODUCT_ID":product_id, "CODE":code}

@get('/product/<cat_ID>')
def get_product(cat_ID):
    status = None
    msg = None
    product = None
    code = None


    try:
        with connection.cursor() as cursor:
            sql = 'SELECT * FROM product WHERE product_ID={}'.format(cat_ID)
            category = cursor.execute(sql)
            result = cursor.fetchone()

        if result:
            product = {"category": result['id'],
                        "description" : result["product_desc"],
                        "price": result["price"],
                        "title": result["title"],
                        "favorite": result["favorite"],
                        "img_url": result["img_url"],
                        "id": result['product_ID']
            }
            status= "SUCCESS"
            code = "200 - product fetched successfully"
        else:
            status = "ERROR"
            code = "404"
            msg = "Product not found"

    except Exception as e:
        if e:
            status = "ERROR"
            msg = "Internal Error"
            code = "500 - internal error"


    return {"STATUS":status,"MSG":msg,"PRODUCT":product,"CODE":code}

@delete('/product/<cat_ID>')
def delete_product(cat_ID):
    result = {
    "STATUS": None,
    "MSG": None,
    "CODE": None
    }

    try:
        with connection.cursor() as cursor:
            sql = 'DELETE FROM product where product_ID={}'.format(cat_ID)
            category = cursor.execute(sql)
            connection.commit()

    except Exception as e:
        if e:
            result['STATUS'] = "ERROR"
            result['MSG'] = "Internal Error"
            result['code'] = "500 - internal error"

    if category != 0:
        result['STATUS'] = "SUCCESS"
        result['CODE'] = "201 - product deleted successfully"

    if category == 0:
        result['STATUS'] = "ERROR"
        result['CODE'] = '404 - product not found'
        result['MSG'] = 'product not found'

    return result

@get('/products')
def list_all_products():
    return_value = {
    "STATUS":None,
    "MSG":None,
    "PRODUCTS":None,
    "CODE":None
    }

    formatted_result = []

    try:
        with connection.cursor() as cursor:
            sql = 'SELECT * FROM product'
            cursor.execute(sql)
            results = cursor.fetchall()

            for result in results:

                product = {"category": result['id'],
                        "description" : result["product_desc"],
                        "price": result["price"],
                        "title": result["title"],
                        "favorite": result["favorite"],
                        "img_url": result["img_url"],
                        "id": result["product_ID"]
                        }
                formatted_result.append(product)

        return_value["STATUS"] = "SUCCESS"
        return_value["PRODUCTS"] = formatted_result
        return_value["CODE"] = "200 - success"

    except Exception as e:
        if e:
            return_value['STATUS'] = "ERROR"
            return_value['MSG'] = "Internal Error"
            return_value['code'] = "500 - internal error"


    return return_value

@get('/category/<cat_ID>/products')
def list_products_by_category(cat_ID):

    return_value = {
    "STATUS":None,
    "MSG":None,
    "PRODUCTS":None,
    "CODE":None
    }

    formatted_result = []

    try:
        with connection.cursor() as cursor:
            sql = 'SELECT * FROM product WHERE id={}'.format(cat_ID)
            cursor.execute(sql)
            results = cursor.fetchall()

            for result in results:

                product = {"category": result['id'],
                        "description" : result["product_desc"],
                        "price": result["price"],
                        "title": result["title"],
                        "favorite": result["favorite"],
                        "img_url": result["img_url"],
                        "id": result["product_ID"]
                        }
                formatted_result.append(product)

        return_value["STATUS"] = "SUCCESS"
        return_value["PRODUCTS"] = formatted_result
        return_value["CODE"] = "200 - success"

        if not results:
            return_value["STATUS"] = "ERROR"
            return_value['MSG'] = "Internal Error"
            return_value["CODE"] = "404 - category not found"

    except Exception as e:
        if e:
            return_value['STATUS'] = "ERROR"
            return_value['MSG'] = "Internal Error"
            return_value['code'] = "500 - internal error"


    return return_value


@get('/js/<filename:re:.*\.js>')
def javascripts(filename):
    return static_file(filename, root='js')

@get('/css/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='css')

@get('/images/<filename:re:.*\.(jpg|png|gif|ico)>')
def images(filename):
    return static_file(filename, root='images')

def main():

    run(host='localhost', port=7000)

if __name__ == '__main__':
    main()