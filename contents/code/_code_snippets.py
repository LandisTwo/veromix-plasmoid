# -*- coding: utf-8 -*-
    def start_effect(self):
        #print Plasma.Animator.__dict__
        #create(Plasma.Animator.PulseAnimation)
        #print Plasma.Animator.PulseAnimation
        #val =  self.animator.customAnimation (1000, 2000, Plasma.Animator.LinearCurve, self.mute , "self.createMeter" )
        #val =  self.animator.animateElement(self.mute, Plasma.Animator.FadeAnimation)
        #print self.animator.create(Plasma.Animator.FadeAnimation)
        #Plasma.Animator.create()
        #QTimer.singleShot(100, self.start_effect)
        #print
        self.animator = Plasma.Animator.self()
        self.pressed = not self.pressed
        self.mute.setPressed(self.pressed)
        QTimer.singleShot(800, self.start_effect)
        #if self.mute.pressed():
            #print "h"
            ##self.animator.animateItem(self.mute, Plasma.Animator.DisappearAnimation)
            #self.mute.setPressed(self.pressed)
            #QTimer.singleShot(800, self.start_effect)
        #else:
            ##
            #print "s"
            #self.mute.setPressed(False)
            #self.animator.animateElement(self.mute, Plasma.Animator.GrowAnimation)
            #self.animator.animateElement(self.mute, Plasma.Animator.AppearAnimation)
            #self.mute.setVisible(True)
            #self.mute.resize(48,48)
            #self.mute.adjustSize()
            #self.mute.setMaximumSize(38,38)
            #self.mute.setMinimumSize(38,38)
            #QTimer.singleShot(1000, self.start_effect)

        #print self.animator.animateItem(self.mute, Plasma.Animator.DisappearAnimation)
        #self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum,True) )
        #self.middle.setVisible(False)
        #self.mute.setVisible(False)
        #self.resize(QSizeF(0,0))
        #self.adjustSize()
        #print "on_double_clicked"




    def on_mute_cb(self ):
        #print Plasma.Animator.self().animateItem(self.meter.graphicsItem(), Plasma.Animator.ActivateAnimation)
        #self.animator = Plasma.Animator.self()
        if self.isMuted():
            #print self.animator.animateItem(self, Plasma.Animator.DisappearAnimation)
            #print self.animator.animateItem(self.middle, Plasma.Animator.DisappearAnimation)
            #print self.animator.animateItem(self.middle, Plasma.Animator.DisappearAnimation)
            self.pa.set_sink_mute(self.index, False)
        else:
            #self.meter.setVisible(True)
            #print self.animator.animateItem(self.meter, Plasma.Animator.AppearAnimation)
            self.pa.set_sink_mute(self.index, True)




######################################

        #self.meter.setMinimumSize(self.mute.minimumSize())
        #self.mute.resize(self.meter.size())

        #self.slider.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum))
        #self.slider.setMinimumSize( QSizeF(300,1))
        #self.slider.resize( QSizeF(800,600))

        #policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum, True)
        ##size = QSizeF(50,50)
        ##self.meter.setMaximumSize(size)
        ##self.meter.setSizePolicy(policy)
        #self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))




                #self.layout.removeItem(self.mute)
        #self.layout.removeItem(self.slider)
        #self.mute.deleteLater()
        #self.mute.setParent(None)
        #self.slider.setParent(None)
        #self.pressed = False
        #self.start_effect()


class Spacer(QGraphicsWidget):

    def paint(self, painter,  option, widget = 0):
        margin = 5
        m_left = margin
        m_top = margin
        m_right = margin
        m_bottom = margin
        painter.setRenderHint(QPainter.Antialiasing)
        p = Plasma.PaintUtils.roundedRectangle(
                            self.contentsRect().adjusted(m_left, m_top, -m_right, -m_bottom), 4)

        c = Plasma.Theme.defaultTheme().color(Plasma.Theme.TextColor)
        c.setAlphaF(0.3)
        painter.fillPath(p, c)
class WidgetGroup(QGraphicsWidget):

    def __init__(self ,sink,  parent):
        QGraphicsWidget.__init__(self)
        self.layout = QGraphicsLinearLayout(Qt.Vertical)
        self.layout.setContentsMargins(0,0,0,0)
        #self.layout.setContentsMargins(6,6,6,6)
        self.setLayout(self.layout)
        self.add()

    def add(self):
        self.child = SinkUI(self.sink, self.parent)
        self.layout.insertItem(0, self.child)
        self.child2 = SinkUI(self.sink, self.parent)
        self.layout.insertItem(0, self.child2)
