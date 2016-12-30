import turtle

def draw():
    window = turtle.Screen()
    window.bgcolor("turquoise")
    
    draw_square()
    draw_circle()
    draw_triangle()

    window.exitonclick()
    
def draw_square():
 
    brad = turtle.Turtle()
    brad.shape("turtle")
    brad.color("white")
    
    turn = 4
    i = 0
    
    while (i < turn):
        brad.forward(100)
        brad.right(90)
        i = i + 1


def draw_circle():
    
    angie = turtle.Turtle()
    angie.color("yellow")
    angie.circle(100)


def draw_triangle():

    alex = turtle.Turtle()
    alex.color("blue")
    alex.right(45)
    alex.forward(100)
    alex.right(105)
    alex.forward(200)
    alex.right(150)
    alex.forward(200)


draw()
