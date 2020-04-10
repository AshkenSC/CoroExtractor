import os
import shutil

def file_rename(path,todir):
        i = 0
        filelist=os.listdir(path)#该文件夹下所有的文件（包括文件夹）
        for files in filelist:
            # i=i+1
            Olddir=os.path.join(path,files)
            if os.path.isdir(Olddir):
                sub_path = path + '/' + filelist[i]
                sub_filelist = os.listdir(sub_path)
                j = 1
                for sub_files in sub_filelist:
                    filename = os.path.splitext(sub_files)[0]  # 文件名
                    newname = 'CENs_'+ filelist[i] + '_' + str(j)
                    newpath = sub_path + '/'
                    j = j + 1
                    os.rename(newpath + filename + ".json", newpath + newname + ".json")
                    shutil.copy(newpath + newname + ".json", todir)
                    
                i = i + 1
            else:
                    continue
path = (r'E:\Monash\Coronavirus\crawler\complementary\alldata')# 全部文件的路径
todir = "E:\Monash\Coronavirus\crawler\complementary\new"  # 存放复制文件的路径
file_rename(path,todir)
