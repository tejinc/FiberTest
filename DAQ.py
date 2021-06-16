import pandas
import numpy as np
import os
import fibertest as ft
from time import sleep
import am_reader as ar

class DAQ(object):
    def __init__(self,n=5):
        self.save_dir = "./"
        
        self.fiber_id = -1
        self.curr_dataframe = pandas.DataFrame()
        """ number of repeated laser movement
        """
        self.SetRepitition(n)

        #status
        #0: New data frame
        #1: Filled dataframe
        self.curr_df_status = 0
        self.curr_save_status= False
        self.curr_save_path = None
        self.ResetDataFrame()

        #board setting
        self.board_initialized = False
        self.board_pos_id = None
        self.board_pos = None

        #ammeter setting
        """ the number of ammeter readings taken at each laser measurement point,
            this is not the number of repeated measurement.
        """
        self.n_measurements = 5 
        # this i
        pass

    #System setting
    def SetRepitition(self, n):
        #Set number of repeated run but do not reset dataframe
        self.run_reptition = n
        self.df_pmt_columns = [ "pmt%02d"%(i+1) for i in range(n) ]
        self.df_det_columns = [ "det%02d"%(i+1) for i in range(n) ]
        self.df_res_columns = [ "pmt_avg", "pmt_stdev", "det_avg","det_stdev"]



    def SetSaveDirectory( self, path ):
        """Setting the directory to save dataframe as csv

        Args:
            path ([str]): "path/to/directory"

        Returns:
            [str]: return save path
        """
        self.save_dir = path
        if not os.path.exists(path):
            print("Directory does not exist, creating new directory")
            os.makedirs(path)
        return self.save_dir

    def SetFiberID( self, ID ):
        self.fiber_id = ID

    #Dataframe operation
    def ResetDataFrame(self, rows=9):
        """Reset dataframe to original mode.
           set status to 0
           Default number of rows is 9
        """
        columns = self.curr_dataframe.columns
        self.curr_dataframe.drop(columns,axis=1,inplace=True)
        columns=["pos","pos_id"]+self.df_pmt_columns+self.df_det_columns+self.df_res_columns

        self.curr_dataframe = pandas.DataFrame()
        for name in columns:
            self.curr_dataframe[name]=np.array( [0.]*rows, float )

        self.curr_df_status = 0
        self.curr_save_status= False
        self.curr_save_path = None

    def SaveDataFrame(self, df, path=None):
        """ Save a dataframe to path
            if path is None, prompt for a path
            if path already exists, prompt for overwrite

        Args:
            df ([DataFrame]):  an arbitrary datafame
            path ([str], optional): Save path. Defaults to None.

        Returns:
            [bool]: True or False, should return Tue all
        """
        try:
            save_path=path
            if save_path is None: 
                p_default = "./fiber_%i.csv"%self.fiber_id
                p = input("Please specify save path or press enter to use the default : %s\n"%p_default)
                save_path = p_default if p=='' else p
    
            #check if path is empty
            if os.path.exists( save_path ):
                key = input( "File already exists. n: specify new path, o:overwrite, q: quit without saving\n" )
                if key.lower()  == "o":
                    pass
                elif key.lower() == "q":
                    print("Data not saved")
                    return False
                else:
                    self.SaveDataFrame(df, None)
                    return
            #df.to_exel( save_path )
            df.to_csv( save_path, index=False )
            print( "Dataframe saved to %s"%save_path)
            return True
        except:
            print("Saving failed.")
            return False

    def SaveCurrentDataFrame(self):
        if self.curr_df_status == 0:
            print("Current dataframe not defined. Exit")
            return -999

        self.curr_save_status = self.SaveDataFrame(self.curr_dataframe,self.curr_save_path)

        return self.curr_save_status
        



    def CreateNewDataFrame(self, fullpath, rows=9):
        """Create new dataframe (actually reset current dataframe)

        Args:
            fname (str): full path
            rows (int): number of rows in each column

        Returns:
            bool: True or False
        """
        if self.curr_df_status == 1 and self.curr_save_status is False:
            save=input("Current dataframe not saved, do you want to save current data frame? y: yes, n:no\n")
            if save.lower() == "y":
                self.SaveDataFrame(self.curr_dataframe)
        
        self.ResetDataFrame(rows)
        self.curr_save_path = fullpath
        return True
        
                
            

    #ammeter setting
    def InitializeAmmeters(self):
        for am in ar.equipments:
            ar.initialize(am,5e-6)

    def ReadAmmeters(self, ncounts=5):
        res=[]
        digital = ar.getAvgStdev( ar.getDigitalReading, ar.equipments[0], ncounts)
        analog = ar.getAvgStdev( ar.getAnalogReading, ar.equipments[1], ncounts)
        return (digital,analog)






    #Board setting
    def InitializeBoard(self, with_board = True):
        ft.no_board = (not with_board)
        if not ft.no_board:
            ft.a_board = ft.board_setup()
            ft.move_initial_home(ft.end_home)
            sleep(5)
        self.board_initialized = True
        self.board_pos_id = int(ft.num_intrv)
        self.board_pos = ft.end_home

    def MoveBoard(self, direction): #direction = F or B
        if not self.board_initialized:
            print( "Board is not initialized. Exit" )
            return -999
        #F: towards end, away from pmt
        #B: towards PMT

        direction = direction.upper()
        if direction == "F" and self.board_pos_id>=int(ft.num_intrv):
            print( "Board already reached the end. Exit." )
            return -999
        if direction == "B" and self.board_pos_id<= 0:
            print( "Board already reached PMT. Exit." )
            return -999

        if direction == "F":
            if not ft.no_board:
                ft.a_board.digitalWrite(ft.b_dir, "LOW")  # #  move forward from home
                ft.a_board.digitalStepper('F', ft.b_dir, ft.b_stp, int(ft.interval))
            self.board_pos_id+=1
            self.board_pos+=ft.interval

        if direction == "B":
            if not ft.no_board:
                ft.a_board.digitalWrite(ft.b_dir, "HIGH")  # #  move forward from home
                ft.a_board.digitalStepper('B', ft.b_dir, ft.b_stp, int(ft.interval))
            self.board_pos_id-=1
            self.board_pos-=ft.interval

        return self.board_pos_id

    def MoveBoardNSteps(self, direction, n_steps):
        if not self.board_initialized:
            print( "Board is not initialized. Exit" )
            return -999
        #F: towards end, away from pmt
        #B: towards PMT

        direction = direction.upper()
        if direction == "F" and self.board_pos_id+n_steps>int(ft.num_intrv):
            print( "Board will exceed the end. Exit." )
            return -999
        if direction == "B" and self.board_pos_id-n_steps< 0:
            print( "Board will exceed PMT. Exit." )
            return -999

        if direction == "F":
            if not ft.no_board:
                ft.a_board.digitalWrite(ft.b_dir, "LOW")  # #  move forward from home
                ft.a_board.digitalStepper('F', ft.b_dir, ft.b_stp, int(ft.interval)*n_steps)
            self.board_pos_id+=n_steps
            self.board_pos+=ft.interval*n_steps

        if direction == "B":
            if not ft.no_board:
                ft.a_board.digitalWrite(ft.b_dir, "HIGH")  # #  move forward from home
                ft.a_board.digitalStepper('B', ft.b_dir, ft.b_stp, int(ft.interval)*n_steps)
            self.board_pos_id-=n_steps
            self.board_pos-=ft.interval*n_steps

        return self.board_pos_id

    def MoveTowardsEnd(self):
        return self.MoveBoard("F")

    def MoveTowardsPMT(self):
        return self.MoveBoard("B")

    def MoveBoardToPosition(self, pos_id):
        move_pos = int(pos_id)
        if pos_id > ft.num_intrv:
            move_pos = ft.num_intrv - 1
            print( "Position exceeded maximum position at %d"%(ft.num_intrv-1) )
        if pos_id < 0:
            move_pos = 0
            print( "Position less han minimum position at 0" )
        

        move_str = "F" if move_pos>self.board_pos_id else "B"
        move_n = abs( self.board_pos_id - move_pos )
        print("moving %d steps"%move_n)

        if self.board_initialized:
            self.MoveBoardNSteps(move_str,move_n)
        
        return self.board_pos_id
    
    def MoveBoardHome(self):
        if self.board_initialized:
            self.MoveBoardToPosition(0)
            sleep(5)
        return

    #DAQ proper
    # want to move 
    def RunDAQ(self, ID, n_rep = 5, save_dir="./data", prefix="fiber", suffix=None, positions=None):
        sID="%06d"%ID
        self.SetSaveDirectory(save_dir)
        fname = "_".join([prefix,sID])
        if suffix is not None: fname = "_".join([fname,suffix])
        fname+=".csv"
        path = self.save_dir+"/"+fname

        #Initialize board and ammeter
        self.InitializeBoard()
        self.InitializeAmmeters()

        sleep(5)

        #Step back
        # repeating measurements N times
        run_range = range(9)[::-1] if positions == None else positions
        rep_count = 1
        print("Run Ranges are: ", run_range)

        #Reset Dataframe
        self.SetRepitition(n_rep)
        self.CreateNewDataFrame(path,len(run_range))



        while( rep_count <= self.run_reptition):
            self.MoveBoardToPosition(run_range[0])
            sleep(5)

            print("rep %d"%rep_count)
            #set dataframe header
            pmt_name = "pmt%02d"%rep_count
            det_name = "det%02d"%rep_count

            print(pmt_name, det_name)
            #Step and record measurement
            for i in range(len(run_range)):
                bp = run_range[i]

                #move laser
                print("Moving laser to %d ..."%bp)
                self.MoveBoardToPosition(bp)
                sleep(1)
                print("Done")
                # take data
                print("Aquiring Reading...")
                digital, analog = self.ReadAmmeters(self.n_measurements)
                #print (digital,analog)

                # copy data to dataframe
                print("Digital: ", digital[0], "Analog: ", analog[0])
                self.curr_dataframe[pmt_name][i] = digital[0]
                self.curr_dataframe[det_name][i] = analog[0]
                self.curr_dataframe["pos"][i] = self.board_pos
                self.curr_dataframe["pos_id"][i] = self.board_pos_id

            rep_count+=1


        #Calculate avg and stdev
        
        self.curr_dataframe["pmt_avg"]= self.curr_dataframe[self.df_pmt_columns].mean(axis=1)
        self.curr_dataframe["det_avg"]= self.curr_dataframe[self.df_det_columns].mean(axis=1)

        self.curr_dataframe["pmt_stdev"]= self.curr_dataframe[self.df_pmt_columns].std(axis=1)
        self.curr_dataframe["det_stdev"]= self.curr_dataframe[self.df_det_columns].std(axis=1)


        #Saving DataFrame
        print(path)
        self.SaveDataFrame(self.curr_dataframe, path)
        #self.ResetDataFrame()

        #Move board home
        self.MoveBoardHome()

        return 0





with_board=True
daq = DAQ()
#print(daq.curr_dataframe)