# 150240721
# Berkay Emre Keskin
# BLG317E

from flask import Blueprint, render_template

main = Blueprint('main', __name__)

# ----------------------------- LANDING ROUTE -----------------------------
@main.route('/')
def index():
    return render_template('landing/landing.html')