import tkinter as tk

import knowledge_tree.constants as constants
from knowledge_tree.point import Point
from knowledge_tree.axes import Axes
from knowledge_tree.graph_manager import GraphManager


class View(object):
    """Manages all of the visible components of the program, including the
    displayed graph.
    
    Attributes:
        main (Main): A reference to the Main instance that contains the View instance
        canvas (tk.Canvas): The canvas on which the visible components will be drawn.
        progress_bar (Bar): A progress bar that displays the progress of calculating the data to
            display
        loading_text (text&): A reference to the text that is displayed above the progress bar
        axes (Axes): A reference to the set of axes that the points will be displayed on
        graph_manager (?): A reference to the GraphManager that manages the plotted points on the axes
        
    Public methods:
        View(main=None)
    """ 

    PROGRESS_BAR_SCALE_MAX = constants.interest_rate_total_steps() * constants.initial_balance_total_steps()
    
    def __init__(self, main=None):
    
        if not main:
            raise ValueError()
            
        self.main = main
        self.canvas = tk.Canvas(
            self.main.root,
            background='#FFFFFF',
            **constants.canvas_dimensions)
        self.progress_bar = Bar(
            self, length=800,
            scale_min=0,
            scale_max=self.PROGRESS_BAR_SCALE_MAX,
            initial_value=0)
        self.axes = Axes(
            canvas=self.canvas,
            **constants.axes_display,
            **constants.axes_scale)
        self.graph_manager = GraphManager(self)
                                
        self.canvas.grid()


class Bar(object):
    """Represents a display bar or gauge on the canvas.
    
    Attributes:
        view (View): A reference to the View instance that this Bar is associated with
        value (numeric)
        orientation (str, property)
        corner (Point): represents the upper-left corner of a horizontal bar
                            or the lower-left corner of a vertical one
        width (int)
        length (int)
        scale_min (int)
        scale_max (int)
        color (str): A hex string representing the color of the bar
        display (rectangle&)
        border (rectangle&)
        
    instance methods:
        Bar( view, orientation='horizontal',
             corner=Point(0 ,0), width=40, length=100,
             scale_min=0, scale_max=10 )
        update( newVal )
    """
    def __init__(self, view, orientation='horizontal',
                 corner=Point(0, 0), width=40, length=100,
                 scale_min=0, scale_max=10, color='#0000FF',
                 initial_value=10):
        # Set internal attributes
        self.view = view
        self.value = initial_value
        self.orientation = orientation
        self.corner = corner
        self.width = width
        self.length = length
        self.scale_min = scale_min
        self.scale_max = scale_max
        self.color = '#0000FF'
        
        # Calculate corner positions
        if self.orientation == 'horizontal':
            upper_left = self.corner.coords()
            lower_right = (self.corner + Point(self.length, self.width)).coords()
        else:
            upper_left = (self.corner + Point(0, -self.length)).coords()
            lower_right = (self.corner + Point(self.width, 0)).coords()
        
        # Place bar on the canvas
        self.display = self.view.canvas.create_rectangle( 
          *upper_left, *lower_right,
          fill=self.color )
        self.border = self.view.canvas.create_rectangle(
          *upper_left, *lower_right,
          width=3)
        
        if initial_value != scale_max:
            self.update(initial_value)
    
    @property
    def orientation(self):
        return self._orientation
    
    @orientation.setter
    def orientation(self, new_val):
        is_valid = (new_val == 'horizontal' or new_val == 'vertical')
        if not is_valid:
            raise ValueError('orientation can only take the values'
                             ' \'horizontal\' or \'vertical\'.')
        self._orientation = new_val
    
    def update(self, newVal):
        """update the length of the bar to reflect the new value"""
        if newVal > self.scale_max or newVal < self.scale_min:
            raise ValueError('The bar\'s maximum or minimum value has been exceeded.')
        
        self.value = newVal
        new_length = int(self.length*newVal/self.scale_max)
        self.view.canvas.itemconfigure( self.display, state=tk.HIDDEN )
        assert self.orientation == 'vertical' or self.orientation == 'horizontal'
        if self.orientation == 'horizontal':
            upper_left = self.corner.coords()
            lower_right = (self.corner + Point(new_length, self.width)).coords()
        else:
            upper_left = (self.corner + Point(0, -new_length)).coords()
            lower_right = (self.corner + Point(self.width, 0)).coords()

        self.display = self.view.canvas.create_rectangle(
          *upper_left, *lower_right,
          fill=self.color)
