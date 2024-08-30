from zarr_libraries import *
from typing import Optional
import numpy as np
import shutil
import matplotlib.axes

class Benchmark:
    def __init__(self, shape: list, chunks: list) -> None:
        self.__shape = shape
        self.__chunks = chunks
        self.__average_bandwidth = {}
        self.__zarr_writers = {
            "TensorStore" : Tensorstore(),
            "Zarr Python" : Zarr_Python(),
            "OME Zarr"    : Ome_Zarr(),
            "Cpp Zarr"    : Cpp_Zarr()
        }
        self.__write_zarr = {}
        self.__append_zarr = {}
        
    
    ''' These functions are intended to be "private" and for use only inside the class '''    
    def __set_write_functions(self, shape: list, zarr_data: np.ndarray) -> None:
        self.__write_zarr = {
            "TensorStore" : lambda: self.__zarr_writers["TensorStore"].write_zarr(shape=shape, chunks=self.chunks, zarr_data=zarr_data),
            "Zarr Python" : lambda: self.__zarr_writers["Zarr Python"].write_zarr(shape=shape, chunks=self.chunks, zarr_data=zarr_data),
            "OME Zarr" : lambda: self.__zarr_writers["OME Zarr"].write_zarr(chunks=self.chunks, zarr_data=zarr_data),
            "Cpp Zarr" : lambda: self.__zarr_writers["Cpp Zarr"].write_zarr(shape=shape, chunks=self.chunks)
        }
        
        
    def __set_append_functions(self,new_shape: list, zarr_data: np.ndarray, multiplier: int) -> None:
        self.__append_zarr = {
            "TensorStore" : lambda: self.__zarr_writers["TensorStore"].append_zarr(shape=self.shape, chunks=self.chunks, new_shape=new_shape, zarr_data=zarr_data, multiplier=multiplier),
            "Zarr Python" : lambda: self.__zarr_writers["Zarr Python"].append_zarr(shape=self.shape, chunks=self.chunks, zarr_data=zarr_data) 
        }
        
    
    def __print_results(self, additional_info: Optional[str] = None):
        if additional_info: print(additional_info)
        
        print(f"Shape {self.shape}, Chunks {self.chunks}")
        print("----------Bandwidth----------")
        for test, bandwidth in self.__average_bandwidth.items():
            print(f"{test} : {bandwidth} GBps")
        print("\n\n")
    
    
    ''' These functions are intended to be "public" and for use outside of the class '''
    @property
    def shape(self) -> list:
        return self.__shape
    
    
    @property
    def chunks(self) -> list:
        return self.__chunks
    
    
    def run_write_tests(self, num_of_gigabytes: int, show_results: bool,
                        choose_lib: Optional[str] = None,
                        graph: Optional[matplotlib.axes._axes.Axes] = None, 
                        avg_graph: Optional[matplotlib.axes._axes.Axes] = None) -> None:
        
        # error checking to see if chosen lib exists in test
        if choose_lib != None and choose_lib not in set(self.__zarr_writers.keys()):
            raise ValueError(f"There is no library of name \"{choose_lib}\".") 
        
        gb_in_bytes = 1073741824 # represents number of bytes in a GB
        
        for lib_name, writer in self.__zarr_writers.items():
            # some libraries fail if there already exists a folder in the path that they are writing to
            if Path(writer.data_path).exists():
                shutil.rmtree(writer.data_path)
        
            # if a specified library is chosen for testing, skip any that isn't that test 
            if choose_lib != None and choose_lib != lib_name: continue
            
            print(f"\n\n--------{lib_name} Stress Test--------\n\n")
            
            multiplier = 1 # multiplier that increases shape of zarr folder written
            curr_data_size = 0 # test will run until curr_data_size reaches specified GB size passed into the function
            write_speeds = []
            file_sizes = []
            
            while curr_data_size < (num_of_gigabytes * gb_in_bytes):
                # modify the append dimension, unpack the rest 
                new_shape = [self.shape[0] * (multiplier), *self.shape[1:]]
                zarr_data = np.empty(())
                
                # Cpp zarr implementation creates data in cpp_zarr.cpp, skip here to avoid making unused data 
                if lib_name != "Cpp Zarr":
                    zarr_data = np.random.randint(low=0, high=256, size=new_shape, dtype=np.uint8)
            
                # returns time taken to write zarr folder 
                self.__set_write_functions(shape=new_shape, zarr_data=zarr_data)
                total_time = self.__write_zarr[lib_name]() # calling a lambda function inside of a dictionary
                
                # prints info to the terminal 
                print(f"Multiplier on first dimension : {multiplier}x\n{lib_name} -> creating zarr : {total_time} seconds")
                print(f"The zarr folder is of size {formatted_folder_size(writer.data_path)}\n\n")
                
                curr_data_size = np.prod(new_shape) # 3d array filled with 1 byte ints so multiplication gives accurate size in bytes
                file_sizes.append(curr_data_size * 10**-9) # converts bytes to GB
                write_speeds.append((curr_data_size * 10**-9) / total_time) # GB/s
        
                # goes from 1 to 5, then adds 5 every time after that
                multiplier += 4 if multiplier == 1 else 5 
                
                shutil.rmtree(writer.data_path)
                
            if graph: graph.plot(file_sizes, write_speeds, label=lib_name, marker='o')
            if avg_graph: avg_graph.bar(lib_name, np.average(write_speeds))  
            self.__average_bandwidth[lib_name + " Write"] = np.average(write_speeds)
            
            print("--------------------------------------------------------------\n\n")
            
        if show_results:
            self.__print_results(additional_info=(f"Write Test GB Soft Cap: {num_of_gigabytes}GB"))


    def run_append_tests(self, num_of_gigabytes: int, show_results: bool,
                        choose_lib: Optional[str] = None,
                        graph: Optional[matplotlib.axes._axes.Axes] = None, 
                        avg_graph: Optional[matplotlib.axes._axes.Axes] = None) -> None:
        
        # error checking to see if chosen lib exists in test
        if choose_lib != None and choose_lib not in set(self.__zarr_writers.keys()):
            raise ValueError(f"There is no library of name \"{choose_lib}\".") 
        
        gb_in_bytes = 1073741824 # represents number of bytes in a GB
        write_size = np.prod(self.shape) # amount of bytes appended on in each function call
        
        for lib_name, writer in self.__zarr_writers.items():
            # these are the only libraries that allow for appending of data
            if lib_name != "TensorStore" and lib_name != "Zarr Python":
                continue
            
            # if a specified library is chosen for testing, skip any that isn't that test
            if choose_lib != None and choose_lib != lib_name: continue  
            
            print(f"\n\n--------{lib_name} Append Stress Test--------\n\n")
            
            multiplier = 1 # multiplier that increases shape of zarr folder written
            curr_data_size = 0 # test will run until curr_data_size reaches specified GB size passed into the function
            write_speeds = []
            write_numbers = []
            
            while curr_data_size < (num_of_gigabytes * gb_in_bytes):
                # modify the append dimension, unpack the rest 
                new_shape = [self.shape[0] * (multiplier), *self.shape[1:]]
                
                # creating new data and adjusting the shape
                zarr_data = np.random.randint(low=0, high=256, size=self.shape, dtype=np.uint8)
                
                # returns time taken to write zarr folder / both libraries use a different approach hence the if statements
                self.__set_append_functions(new_shape=new_shape, zarr_data=zarr_data, multiplier=multiplier)
                total_time = self.__append_zarr[lib_name]() # calling a lambda function inside of a dictionary

                # prints info to the terminal 
                print(f"Multiplier on first dimension : {multiplier}x\n{lib_name} -> appending zarr : {total_time} seconds")
                print(f"The zarr folder is of size {formatted_folder_size(writer.data_path)}\n\n")
                
                curr_data_size = np.prod(new_shape) # 3d array filled with 1 byte ints so multiplication gives accurate size in bytes
                write_numbers.append(multiplier) # converts bytes to GB
                write_speeds.append((write_size * 10**-9) / total_time) # GB/s
        
                multiplier += 1
                
            shutil.rmtree(writer.data_path) 
                
            if graph: graph.plot(write_numbers, write_speeds, label=lib_name)
            if avg_graph: avg_graph.bar(lib_name, np.average(write_speeds))
            self.__average_bandwidth[lib_name + " Append"] = np.average(write_speeds)
            
            print("--------------------------------------------------------------\n\n")
            
        if show_results:
            self.__print_results(additional_info=(f"Write Test GB Soft Cap: {num_of_gigabytes}GB"))
    
    
    def run_all_tests(self, append_test_gigabytes: int, write_test_gigabytes: int, 
                      choose_lib: Optional[str] = None,
                      append_graph: Optional[matplotlib.axes._axes.Axes] = None, append_avg_graph: Optional[matplotlib.axes._axes.Axes] = None,
                      write_graph: Optional[matplotlib.axes._axes.Axes] = None, write_avg_graph: Optional[matplotlib.axes._axes.Axes] = None) -> None:
        
        self.run_append_tests(num_of_gigabytes=append_test_gigabytes, show_results=False, choose_lib=choose_lib, graph=append_graph, avg_graph=append_avg_graph)
        self.run_write_tests(num_of_gigabytes=write_test_gigabytes, show_results=False, choose_lib=choose_lib, graph=write_graph, avg_graph=write_avg_graph)
        self.__print_results(additional_info=(f"Write Test GB Soft Cap: {write_test_gigabytes}GB | Append Test GB Soft Cap: {append_test_gigabytes}GB"))
    