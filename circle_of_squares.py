import turtle

def draw():
    window = turtle.Screen()
    window.bgcolor("turquoise")

    brad = turtle.Turtle()
    brad.color("white")
    brad.shape("turtle")
    brad.speed(0.5)

    for i in range(0,72):
        draw_square(brad)
        brad.right(5)

    window.exitonclick()
    

def draw_square(st):
 
    turn = 4
    i = 0

    while(i < turn):
        st.forward(100)
        st.right(90)
        i = i+1
    
    
draw()
