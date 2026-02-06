import eel

eel.init('web')

@eel.expose
def py_hello():
    return "Hello from Python!"

if __name__ == '__main__':
    eel.start('pages/welcome.html', size=(1400, 900), port=8000)
