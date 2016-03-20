#! /usr/bin/env python
#-*- coding: utf8 -*-
'This module is used as dashboard for automation testing '
import os
import sys
import time
import unittest
import logging
import platform
import smbc
import commands
import argparse



class AutomationTestDashboard(object):

    samba_directory = {"smoke_test"    :"smb://172.29.51.18/共享/自动化测试用例/冒烟测试每日构建(新)/",
                       "function_test" :"smb://172.29.51.18/共享/自动化测试用例/功能性自动化测试（每日构建）/",
                       "base_test"   :"smb://172.29.51.18/共享/自动化测试用例/压力测试构建/",
                       "stability_test":"smb://172.29.51.18/共享/自动化测试用例/稳定性&可靠性测试(每日构建)/",
                       "shell_test"    :"smb://172.29.51.18/共享/自动化测试用例/Shell脚本/",
                       "component_test"   :"smb://172.29.51.18/共享/自动化测试用例/Python脚本/"
                       }

    scripts_number  = {"smoke_test"       :0,
                       "function_test"    :0,
                       "base_test"        :0,
                       "stability_test"   :0,
                       "shell_test"       :0,
                       "component_test"   :0
                       }

    menu            = [
                       "Smoke Test",
                       "Function Test",
                       "Base Test",
                       "Stability Test",
                       "Component Test",
                       "Shell Test",
                       "All Test",
                       "Scripts Numbers Statistics"
                       ]
            
    Total_number   = 0
    source ="svn"


    def __init__(self):
        self.LoggingConfig()


    def get_working_dir(self,test_type=""):
        'Create local working directory if there is no working directory'
        target_dir =  "/home/"+os.getlogin()+"/automation_testing"
        if test_type == "":
            if os.path.exists(target_dir):
                return target_dir
            else:
                os.mkdir(target_dir)
                return target_dir          
        sub_dir = target_dir+os.sep+test_type+os.sep
        
        if os.path.exists(target_dir):
            if os.path.exists(sub_dir):
                return sub_dir
            else:
                os.mkdir(sub_dir)
        else:
            os.mkdir(target_dir)
            os.mkdir(sub_dir)

        return sub_dir




    def get_samba_dir(self,test_type):
        'Get samba directory according to the test type.'
        return self.samba_directory[test_type]


    def get_files_list_from_dir(self,dir,ext = None):
        allfiles = []
        needExtFilter = (ext != None)
        for root,dirs,files in os.walk(dir):
            for filespath in files:
                filespath = os.path.join(root,filespath)
                extension = os.path.splitext(filespath)[1][1:]
                if needExtFilter and extension in ext:
                    allfiles.append(filespath)
                elif not needExtFilter:
                    allfiles.append(filespath)
        return allfiles


        

    def get_newest_file(self,test_type):
      
        directory_name = self.get_samba_dir(test_type)
        ctx = smbc.Context()
        entries = ctx.opendir(directory_name).getdents()
        name_list = []
        
        if test_type == "smoke_test":
            name_list = [''.join(list(str(entry))[21:112]) for entry in entries if "[冒烟]部件集成测试-自动化测试用例-版本" in str(entry)]
        elif test_type == "function_test":
            name_list = [''.join(list(str(entry))[21:102]) for entry in entries if "功能测试_自动化测试用例-版本" in str(entry)]
        elif test_type == "base_test":
            name_list = [''.join(list(str(entry))[21:98]) for entry in entries if "压力测试_自动化测试用例-版本" in str(entry)]
        elif test_type == "stability_test":
            name_list = [''.join(list(str(entry))[21:110]) for entry in entries if "稳定性可靠性测试_自动化测试用例" in str(entry)]
        elif test_type == "component_test" :
            name_list = [''.join(list(str(entry))[21:37]) for entry in entries]
        elif test_type == "shell_test":
            name_list = [''.join(list(str(entry))[21:36]) for entry in entries]
        else:
            return None

        return str(max((name_list)))

        
                

    def get_scripts_number(self,test_type):
        'get the files number from local directory '

        if test_type == "component_test":
            lst1 = self.get_files_list_from_dir(self.get_working_dir(test_type),"robot")
            lst2 = [x for x in lst1 if x.endswith(".py")]
        elif test_type == "shell_test":
            lst1 = self.get_files_list_from_dir(self.get_working_dir(test_type),"sh")
            lst2 = [x for x in lst1 if x.endswith(".sh")]
        else:
            lst1 = self.get_files_list_from_dir(self.get_working_dir(test_type),"robot")
            lst2 = [x for x in lst1 if not x.endswith("__init__.robot")]     

        self.scripts_number[test_type] = len(lst2)


    
        

    def get_test_scripts_from_samba(self,test_type,latest_file_name):
        remote_file = self.get_samba_dir(test_type)+latest_file_name
        print("%s:\t\t\t%s" % (test_type,remote_file))
        #self.get_files_from_samba(remote_file_name,self.get_working_dir(test_type))
        ctx = smbc.Context()       
        assert remote_file != None,"remote file is null"
 
        sfile = ctx.open(remote_file,os.O_RDONLY)
        os.chdir(self.get_working_dir(test_type))     
        commands.getstatusoutput("rm -fr * ")
        dfile = open(self.get_working_dir(test_type)+"target.zip",'wb')

        #copy file and flush
        dfile.write(sfile.read())
        dfile.flush()
        sfile.close()
        dfile.close()
        os.chdir(self.get_working_dir(test_type))
        
        commandline ="unzip  "+self.get_working_dir(test_type)+"target.zip"
        commands.getstatusoutput(commandline)



    def get_test_scripts_from_svn(self):        
        os.chdir("/home/"+os.getlogin()+"/自动测试/9-全面测试（新）") 
        file_list = os.listdir(os.getcwd())
        newest_file=str(max([entry for entry in file_list if "自动化测试项目-全面测试--日期" in str(entry)]))

        os.chdir(self.get_working_dir())     
        commands.getstatusoutput("rm -fr * ")
        command = "cp "+"/home/"+os.getlogin()+"/自动测试/9-全面测试（新）"+os.sep+newest_file+"  "+self.get_working_dir()+os.sep
        commands.getstatusoutput(command)
        command = "unzip"+" "+newest_file 
        commands.getstatusoutput(command)
        inner_dir = "/home/"+os.getlogin()+"/automation_testing/git-opdog/opdog/TestCases/CDOS2.0"
        #smoke
        command ="cp -fr "+inner_dir+'/冒烟测试'+'   '+self.get_working_dir("smoke_test")
        commands.getstatusoutput(command)
        #function
        command ="cp -fr "+inner_dir+'/功能测试'+'   '+self.get_working_dir("function_test")
        commands.getstatusoutput(command)
        #stress and stability
        command ="cp -fr "+inner_dir+'/稳定性和可靠性测试'+'   '+self.get_working_dir("stability_test")
        commands.getstatusoutput(command)
        #basic
        command ="cp -fr "+inner_dir+'/基础测试'+'   '+self.get_working_dir("base_test")
        commands.getstatusoutput(command)
        #component
        command ="cp -fr "+inner_dir+'/部件测试'+'   '+self.get_working_dir("component_test")
        commands.getstatusoutput(command)




    def empty_working_dir(self,test_type):
        os.chdir(self.get_working_dir(test_type))     
        commands.getstatusoutput("rm -fr * ")
        



    def common_run_test(self,test_type):
        'run the loccal test scripts.move the test result to a spefified local directory.'
        self.empty_working_dir(test_type)
        file_name = self.get_newest_file(test_type)
        self.get_test_scripts_from_samba(test_type,file_name)
        os.chdir(self.get_working_dir(test_type))
        #print(commands.getstatusoutput("sudo sh run_testcases.sh"))
        


    def common_test(self,test_type):
        if self.source == "samba":
            file_name = self.get_newest_file(test_type)
            assert file_name != None,"remote file is null"
            self.get_test_scripts_from_samba(test_type,file_name)
        elif self.source =="svn":
            self.get_test_scripts_from_svn()

        self.get_scripts_number(test_type)
        self.empty_working_dir(test_type)
        


    def ArgumentParser(self):
        #args = parser.parse_args()
        #if args.verbose:
        #    logging.getLogger('').setLevel(logging.DEBUG)
        #else:
        #    logging.getLogger('').setLevel(logging.ERROR)

    
        #logging.debug(self.local_working_dir)
        #logging.info(self.local_working_dir)
        #logging.warning(self.local_working_dir)

        parser = argparse.ArgumentParser(description = 'i am ok')
        parser.add_argument('-v','--verbose',action='store_true',dest='verbose',help='Enable debug info')
        parser.add_argument("-p",'--port',help="caculate square",type=int)


        args = parser.parse_args()
        if args.verbose:
            logging.getLogger('').setLevel(logging.DEBUG)
        else:
            logging.getLogger('').setLevel(logging.INFO)

        if args.port:
            print(args.port**2)

        pass



    def LoggingConfig(self):
        # logging 
        logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a,%d %b %Y %H:%M:%S',
                    filename='scripts_number_checking.log',
                    filemode='w'
                    )

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)-12s: %(levelname) -8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)


        
    def scripts_statistics(self):
        for item in list(self.scripts_number.keys()):
            self.common_test(item)


    def line_statistics(self):
        lst1 = self.get_files_list_from_dir("/home/"+os.getlogin()+"/automation_testing/git-opdog","robot")


        lst3 = [x for x in lst1 if not x.endswith("__init__.robot")]
        lst4 = [x for x in lst3 if 'Keywords' not in x]
        lst2 = [x for x in lst4 if x.endswith(".robot")]

        for i in range(len(lst2)):
            pass
            #print(lst2[i])

        print("From big picture,Total number is %d"%len(lst2))

        total_line =0
        for item in lst2:
            count=len(open(item,'rU').readlines())
            total_line=total_line+count

        print("From big picture,Total code line is %d" % (total_line))

        

    def statistics_caculate(self):
        print('-'*50)
        self.Total_number = sum(list(self.scripts_number.values()))
        for item in self.scripts_number:
            print ("%s:\t\t%10s" %(item,self.scripts_number[item]))
        print("Total test \t\t%10d" % (self.Total_number))
        print('-'*50)

    def print_header(self):
            print('-'*50)
            print(' '*12)
            print(' '*12)
            print("CDOS Test Suite v0.0.1")
            print(' '*12)
            print(' '*12)
            print(' '*12+'Automation Test Dashboard  (%s)' % (self.source))
        


    def main(self):

        self.ArgumentParser()       

        flag = True
        while flag:
            self.print_header()
            for i in range(len(self.menu)):
                print ("%d \t %s" %((i+1),self.menu[i])) 
            print('-'*50) 

            num_1 = raw_input("please input the number ,q is for quit: ").strip()
            
            if num_1 == 'q':
                flag = False
                break

            if num_1.isdigit() and int(num_1) in [1,2,3,4,5,6,7,8]:
                num_1 = int(num_1)
                print("choosed menu is %d,caculateing..." % (num_1))
                print('-'*50)
                
                if num_1 == 1:
                    self.common_run_test("smoke_test")
                elif num_1 == 2:
                    self.common_run_test("function_test")
                elif num_1 == 3:
                    self.common_run_test("base_test")
                elif num_1 == 4:
                    self.common_run_test("stability_test")
                elif num_1 == 5:
                    self.common_run_test("component_test")
                elif num_1 == 6:
                    self.common_run_test("shell_test")
                elif num_1 == 7:
                    self.common_run_test("smoke_test")
                    self.common_run_test("function_test")
                    self.common_run_test("base_test")
                    self.common_run_test("stability_test")
                    self.common_run_test("component_test")
                    self.common_run_test("shell_test")
                    self.common_run_test("shell_test")
                elif num_1 == 8:
                    self.scripts_statistics()
                    self.statistics_caculate()
                    self.line_statistics()
            else:
                continue
            

    def debugFunction(self):
        self.common_run_test("smoke_test")
        pass               
            


if __name__ == "__main__":
    runner = AutomationTestDashboard()
    runner.main()
    #runner.debugFunction()

    sys.exit()


