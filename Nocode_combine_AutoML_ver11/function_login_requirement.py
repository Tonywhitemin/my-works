from flask import Flask, render_template, request, redirect, session, url_for
from functools import wraps

# 自定义装饰器：检查用户是否已登录
# 230620新增
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("db_homepage_login"))  # 重定向到登录页面
        else:
            print("user_id為：",session["user_id"])
        return f(*args, **kwargs)
    return decorated_function