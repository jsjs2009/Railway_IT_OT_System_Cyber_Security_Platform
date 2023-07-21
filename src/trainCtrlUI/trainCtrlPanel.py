#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        uiPanel.py
#
# Purpose:     This module is used to create different function panels.
# Author:      Yuancheng Liu
#
# Created:     2020/01/10
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------
import os
import wx
import wx.grid

from datetime import datetime
import trainCtrlGlobal as gv

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
class PanelTrain(wx.Panel):
    """ Mutli-information display panel used to show all sensors' detection 
        situation on the office top-view map, sensor connection status and a 
        wx.Grid to show all the sensors' basic detection data.
    """
    def __init__(self, parent):
        """ Init the panel."""
        wx.Panel.__init__(self, parent, size=(650, 300))
        self.SetBackgroundColour(wx.Colour(39, 40, 62))
        self.SetSizer(self._buidUISizer())

#--PanelMultInfo---------------------------------------------------------------
    def _buidUISizer(self):
        """ Build the UI with 2 columns.left: Map, right: sensor data Grid."""
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        flagsL = wx.LEFT
        sizer.AddSpacer(5)

        vbox0 = wx.BoxSizer(wx.VERTICAL)

        font = wx.Font(12, wx.DECORATIVE, wx.BOLD, wx.BOLD)
        label = wx.StaticText(self, label="Train Information")
        label.SetFont(font)
        label.SetForegroundColour(wx.Colour("WHITE"))
        vbox0.Add(label, flag=flagsL, border=2)
        vbox0.AddSpacer(10)

        self.grid = wx.grid.Grid(self, -1)
        self.grid.CreateGrid(12, 6)
        # Set the Grid size.
        self.grid.SetRowLabelSize(40)
        #self.grid.SetColSize(0, 50)
        #self.grid.SetColSize(1, 65)
        #self.grid.SetColSize(2, 65)
        # Set the Grid's labels.
        self.grid.SetColLabelValue(0, 'Train-ID')
        self.grid.SetColLabelValue(1, 'Railway-ID')
        self.grid.SetColLabelValue(2, 'Speed[km/h]')
        self.grid.SetColSize(2, 100)
        self.grid.SetColLabelValue(3, 'Current[A]')
        self.grid.SetColSize(3, 100)
        self.grid.SetColLabelValue(4, 'DC-Voltage[V]')
        self.grid.SetColSize(4, 120)
        self.grid.SetColLabelValue(5, 'Power-State')
        self.grid.SetColSize(5, 120)
        vbox0.Add(self.grid, flag=flagsL, border=2)
        sizer.Add(vbox0, flag=flagsL, border=2)
        return sizer

#--PanelMultInfo---------------------------------------------------------------
    def updateSensorIndicator(self, idx, state):
        """ Update the sensor indictor's status Green:online, Gray:Offline."""
        color = wx.Colour("GREEN") if state else wx.Colour(120, 120, 120)
        self.senIndList[idx].SetBackgroundColour(color)

#--PanelMultInfo---------------------------------------------------------------
    def updateSensorGrid(self, idx, dataList):
        """ Update the sensor Grid's display based on the sensor index. """
        if len(dataList) != 3:
            print("PanelMultInfo: Sensor Grid fill in data element missing.")
            return
        # Udpate the grid cells' data.
        totPllNum = totPllAvg = 0
        for i, item in enumerate(dataList):
            dataStr = "{0:.4f}".format(item) if isinstance(
                item, float) else str(item)
            self.grid.SetCellValue(idx, i, dataStr)
            if i == 1: totPllNum += item
            if i == 2: totPllAvg += item
        # update the total numbers. 
        self.grid.SetCellValue(4, 0, str(self.sensorCount))
        self.grid.SetCellValue(4, 1, "{0:.4f}".format(totPllNum))
        self.grid.SetCellValue(4, 2, "{0:.4f}".format(totPllAvg))
        self.grid.ForceRefresh()  # refresh all the grid's cell at one time ?


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelPLC(wx.Panel):
    """ PLC panel UI to show PLC input feedback state and the relay connected 
        to the related output pin.
    """
    def __init__(self, parent, name, ipAddr):
        """ Init the panel."""
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        # Init self paremeters
        self.plcName = name
        self.ipAddr = ipAddr
        self.regsNum = 16
        self.coilsNum = 8
        self.connected = {'0': 'Unconnected', '1': 'Connected'}
        self.gpioInList = [0]*self.regsNum  # PLC GPIO input stuation list.
        self.gpioInLbList = []  # GPIO input device <id> label list.
        self.gpioOuList = [0]*self.coilsNum # PLC GPIO output situation list.
        self.gpioOuLbList = []  # GPIO output device <id> label list.
        # Init the UI.
        self.SetSizer(self.buidUISizer())
        #self.Layout() # must call the layout if the panel size is set to fix.

#--PanelPLC--------------------------------------------------------------------
    def buidUISizer(self):
        """ Build the UI and the return the wx.sizer. """
        mSizer = wx.BoxSizer(wx.VERTICAL) # main sizer
        flagsR = wx.LEFT
        mSizer.AddSpacer(5)
        # Row idx = 0 : set the basic PLC informaiton.
        self.nameLb = wx.StaticText(
            self, label=" PLC Name: ".ljust(15)+self.plcName)
        mSizer.Add(self.nameLb, flag=flagsR, border=5)
        self.ipaddrLb = wx.StaticText(
            self, label=" PLC IPaddr: ".ljust(15)+self.ipAddr)
        mSizer.Add(self.ipaddrLb, flag=flagsR, border=5)
        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        hbox0.Add(wx.StaticText(self, label="Connection:".ljust(15)),
                  flag=flagsR, border=5)
        self.connLb = wx.StaticText(self, label=self.connected['0'])
        hbox0.Add(self.connLb, flag=flagsR, border=5)
        mSizer.Add(hbox0, flag=flagsR, border=5)
        mSizer.AddSpacer(10)
        # Row idx = 1: set the GPIO and feed back of the PLC. 
        mSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(220, -1),
                                 style=wx.LI_HORIZONTAL), flag=flagsR, border=5)
        mSizer.AddSpacer(10)
        # - row line structure: Input indicator | output label | output button with current status.
        for i in range(self.regsNum):
            hsizer = wx.BoxSizer(wx.HORIZONTAL)
            # M221 doc: IO 0:3 are regular input, IO 4:7 are fast input.
            # Col idx = 0: PLC input indicators.
            lbtext = " R_%H 0."+str(i)
            inputLb = wx.StaticText(self, label=lbtext.ljust(12))
            inputLb.SetBackgroundColour(wx.Colour(120, 120, 120))
            hsizer.Add(inputLb, flag=flagsR, border=5)
            self.gpioInLbList.append(inputLb)
            # Col idx =1: PLC output labels.
            hsizer.AddSpacer(15)
            if i < self.coilsNum:
                hsizer.Add(wx.StaticText(self, label=str(
                    " %Q 0."+str(i)+':').ljust(12)), flag=flagsR, border=5)
                # Col idx =2: PLC output ON/OFF contorl buttons.
                hsizer.AddSpacer(5)
                outputBt = wx.Button(self, label='OFF', size=(50, 17), name=self.plcName+':'+str(i))
                #outputBt.Bind(wx.EVT_BUTTON, self.relayOn)
                self.gpioOuLbList.append(outputBt)
                hsizer.Add(outputBt, flag=flagsR, border=5)
            mSizer.Add(hsizer, flag=flagsR, border=5)
            mSizer.AddSpacer(3)
        return mSizer

#--PanelPLC--------------------------------------------------------------------
    def relayOn(self, event): 
        """ Turn on the related ralay based on the user's action and update the 
            button's display situation.
        """
        obj = event.GetEventObject()
        print("PLC panel:   Button idx %s" % str(obj.GetName()))
        plcIdx = int(obj.GetName().split('[')[0][-1])
        outIdx = int(obj.GetName().split(':')[-1])
        # toggle output state.
        self.gpioOuList[outIdx] = 1 - self.gpioOuList[outIdx]
        self.updateOutput(outIdx, self.gpioOuList[outIdx])
        # Update the element on the map.
        tag = str((plcIdx+1)*100+outIdx)
        for element in gv.iPowCtrlPanel.powerLabel:
            if tag in element:
                gv.iMapMgr.setSignalPwr(element, self.gpioOuList[outIdx])
                break

#--PanelPLC--------------------------------------------------------------------
    def setConnection(self, state):
        """ Update the connection state on the UI. 0 - disconnect 1- connected
        """
        self.connLb.SetLabel(self.connected[str(state)])
        self.connLb.SetBackgroundColour(
            wx.Colour('GREEN') if state else wx.Colour(120, 120, 120))
        self.Refresh(False)

    def updateHoldingRegs(self, regList):
        if regList is None or self.gpioInList == regList: return # no new update
        for idx in range(min(self.regsNum, len(regList))):
            status = regList[idx]
            if self.gpioInList[idx] != status:
                self.gpioInList[idx] = status
                self.gpioInLbList[idx].SetBackgroundColour(
                    wx.Colour('GREEN') if status else wx.Colour(120, 120, 120))
        #self.Refresh(False)

    def updateCoils(self, coilsList):
        if coilsList is None or self.gpioOuList == coilsList: return  
        for idx in range(min(self.coilsNum, len(coilsList))):
            status = coilsList[idx]
            if self.gpioOuList[idx] != status:
                self.gpioOuList[idx] = status
                self.gpioOuLbList[idx].SetLabel('ON' if status else 'OFF')
                self.gpioOuLbList[idx].SetBackgroundColour(
                    wx.Colour('GREEN') if status else wx.Colour(253, 253, 253))
        #self.Refresh(False)

    def updataPLCdata(self):
        if gv.idataMgr:
            plcdata =  gv.idataMgr.getPLCInfo(self.plcName)
            if plcdata:
                self.updateHoldingRegs(plcdata[0])
                self.updateCoils(plcdata[1])

    
    def updateDisplay(self, updateFlag=None):
        """ Set/Update the display: if called as updateDisplay() the function will 
            update the panel, if called as updateDisplay(updateFlag=?) the function
            will set the self update flag.
        """
        self.Refresh(False)

#--PanelPLC--------------------------------------------------------------------
    def updateInput(self, idx, status): 
        """ Update the input state for each PLC input indicator."""
        if idx >= 8 or not status in [0,1]: 
            print("PLC panel:   the input parameter is not valid") 
            return
        elif self.gpioInList[idx] != status:
            self.gpioInList[idx] = status
            # Change the indicator status.
            self.gpioInLbList[idx].SetBackgroundColour(
                wx.Colour('GREEN') if status else wx.Colour(120, 120, 120))
            self.Refresh(False) # needed after the status update.

#--PanelPLC--------------------------------------------------------------------
    def updateOutput(self, idx, status):
        """ Update the output state for each PLC output button."""
        if idx >= 8 or not status in [0,1]: 
            print("PLC panel:   the output parameter is not valid") 
            return
        elif self.gpioOuList[idx] != status:
            self.gpioOuList[idx] = status
            [lbtext, color] = ['ON', wx.Colour('Green')] if status else [
            'OFF', wx.Colour(200, 200, 200)]
            self.gpioOuLbList[idx].SetLabel(lbtext)
            self.gpioOuLbList[idx].SetBackgroundColour(color)
            self.Refresh(False) # needed after the status update.

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelTainCtrl(wx.Panel):
    """ Train control Panel control panel."""

    def __init__(self, parent, trackID, trainID, bgColor=wx.Colour(200, 210, 200)):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(bgColor)
        self.trackID = trackID
        self.trainID = trainID
        self.SetSizer(self._buidUISizer())

#-----------------------------------------------------------------------------
    def _buidUISizer(self):
        """ build the control panel sizer. """
        flagsL = wx.LEFT
        startBmp = wx.Bitmap(os.path.join(gv.IMG_FD, 'reset32.png'), wx.BITMAP_TYPE_ANY)
        stoptBmp = wx.Bitmap(os.path.join(gv.IMG_FD, 'emgStop32.png'), wx.BITMAP_TYPE_ANY)
        font = wx.Font(11, wx.DECORATIVE, wx.BOLD, wx.BOLD)
        vbox = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, label=" %s - %s" %(self.trackID, str(self.trainID)))
        label.SetFont(font)
        label.SetForegroundColour(wx.WHITE)
        vbox.Add(label, flag=flagsL, border=2)

        vbox.Add(wx.StaticLine(self, wx.ID_ANY, size=(90, -1),
                                 style=wx.LI_HORIZONTAL), flag=flagsL, border=2)
        vbox.AddSpacer(2)
        hbox0 =  wx.BoxSizer(wx.HORIZONTAL)
        # Add the start button.
        self.recbtn1 = wx.BitmapButton(self, bitmap=startBmp,
                                       size=(startBmp.GetWidth()+10, startBmp.GetHeight()+10))
        self.recbtn1.Bind(wx.EVT_BUTTON, self.startTrain)
        hbox0.Add(self.recbtn1, flag=flagsL, border=2)
        # Add the emergency stop button.
        self.recbtn2 = wx.BitmapButton(self, bitmap=stoptBmp,
                                       size=(stoptBmp.GetWidth()+10, stoptBmp.GetHeight()+10))
        self.recbtn2.Bind(wx.EVT_BUTTON, self.stopTrain)
        hbox0.Add(self.recbtn2, flag=flagsL, border=2)
        hbox0.AddSpacer(5)
        vbox.Add(hbox0, flag=flagsL, border=2)
        return vbox
    
    #-----------------------------------------------------------------------------
    def startTrain(self, event):
        event.GetEventObject().GetId() 
        if gv.iMapMgr:
            gv.gDebugPrint('Start train: %s on track: %s' %(str(self.trainID), self.trackID))
            trains = gv.iMapMgr.getTrains(trackID=self.trackID)
            trainAgent = trains[self.trainID]
            trainAgent.setEmgStop(False)

    #-----------------------------------------------------------------------------
    def stopTrain(self, event):
        if gv.iMapMgr:
            gv.gDebugPrint('Stop train: %s on track: %s' %(str(self.trainID), self.trackID))
            trains = gv.iMapMgr.getTrains(trackID=self.trackID)
            trainAgent = trains[self.trainID]
            trainAgent.setEmgStop(True)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelCtrl(wx.Panel):
    """ Function control panel."""

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.gpsPos = None
        self.SetSizer(self._buidUISizer())

#--PanelCtrl-------------------------------------------------------------------
    def _buidUISizer(self):
        """ build the control panel sizer. """
        flagsR = wx.CENTER
        ctSizer = wx.BoxSizer(wx.VERTICAL)
        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        ctSizer.AddSpacer(5)
        # Row idx 0: show the search key and map zoom in level.
        hbox0.Add(wx.StaticText(self, label="Control panel".ljust(15)),
                  flag=flagsR, border=2)
        ctSizer.Add(hbox0, flag=flagsR, border=2)
        return ctSizer

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    """ Main function used for local test debug panel. """

    print('Test Case start: type in the panel you want to check:')
    print('0 - PanelImge')
    print('1 - PanelCtrl')
    #pyin = str(input()).rstrip('\n')
    #testPanelIdx = int(pyin)
    testPanelIdx = 1    # change this parameter for you to test.
    print("[%s]" %str(testPanelIdx))
    app = wx.App()
    mainFrame = wx.Frame(gv.iMainFrame, -1, 'Debug Panel',
                         pos=(300, 300), size=(640, 480), style=wx.DEFAULT_FRAME_STYLE)
    if testPanelIdx == 0:
        testPanel = PanelImge(mainFrame)
    elif testPanelIdx == 1:
        testPanel = PanelTrain(mainFrame)
    mainFrame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()


