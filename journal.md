# A place to keep my ideas and problems I encounter throughout

## Intitial thoughts
Some questions arise about this project, starting this out im curious on how we use the matricies for RGB values to handoff to the Neural Network to identify against different backgrounds, hands orientation, and skin colors. 
Media Pipe seems to be the main driver for this project, where the program will capture frames from a live feed and pass that through MediaPipe. MP (Media Pipe) then passes an x,y value for list of different identified coordinates. When that is returned we can identify a gesture to then activate a command. 