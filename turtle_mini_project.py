import turtle

def draw():
    window = turtle.Screen()
    window.bgcolor("turquoise")

    brad = turtle.Turtle()
    brad.color("white")
    brad.shape("turtle")
    brad.speed(0.01)
    
    for i in range (1, 73):
        draw_diamond(brad)
        brad.right(5)
    brad.right(90)
    brad.forward(400)
    window.exitonclick()


def draw_diamond(diamond):

        diamond.left(90)
        diamond.forward(90)
        diamond.right(30)
        diamond.forward(100)
        diamond.right(150)
        diamond.forward(100)
        diamond.right(30)
        diamond.forward(90)

draw()
