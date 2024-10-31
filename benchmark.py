from zarr_libraries import *
from typing import Optional
from collections import defaultdict
import numpy as np
import shutil
import matplotlib.axes

class Benchmark:
    def __init__(self, shape: list, chunks: list) -> None:
        self.__shape = shape
        self.__chunks = chunks
        self.__average_bandwidth = {}
        self.__zarr_writers = {
            "TensorStore"  : Tensorstore(),
            "Zarr Python"  : Zarr_Python(),
            "OME Zarr"     : Ome_Zarr(),
            "Cpp Zarr"     : Cpp_Zarr(),
            "Acquire Zarr" : AcquireZarr()
        }
        
    
    ''' These functions are intended to be "private" and for use only inside the class '''        
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
        if choose_lib is not None and choose_lib not in set(self.__zarr_writers.keys()):
            raise ValueError(f"There is no library of name \"{choose_lib}\".") 
        
        gb_in_bytes = 1073741824         # represents number of bytes in a GB
        multiplier = 1                   # multiplier that increases shape of zarr folder written
        curr_data_size = 0               # test will run until curr_data_size reaches specified GB size passed into the function
        write_speeds = defaultdict(list) # dict that holds the write speeds for every lib tested
        file_sizes = []                  # keeps track of the size of data written for graphing purposes
        
        print(f"\n\n--------Write Stress Test--------\n\n")
        
        while curr_data_size < (num_of_gigabytes * gb_in_bytes):
            # modify the append dimension, unpack the rest 
            new_shape = [self.shape[0] * (multiplier), *self.shape[1:]]
            
            # 3d array filled with 1 byte ints so multiplication gives accurate size in bytes
            curr_data_size = np.prod(new_shape)
            
            # creating new data and adjusting the shape
            zarr_data = np.random.randint(low=0, high=256, size=new_shape, dtype=np.uint8)
            
            print("--------------------------------------------------------------------")
            print(f"Current shape : {new_shape} | Current multiplier {multiplier}x")
            print("--------------------------------------------------------------------")
            
            for lib_name, writer in self.__zarr_writers.items():
                # ensures data doesn't already exists
                if Path(writer.data_path).exists():
                    shutil.rmtree(writer.data_path)
                    
                # if a specified library is chosen for testing, skip any that isn't that test
                if choose_lib is not None and choose_lib != lib_name: 
                    continue 
                
                # store time taken to write zarr
                if lib_name in ("TensorStore", "ZarrPython", "Acquire Zarr"):
                    total_time = writer.write_zarr(shape=new_shape, chunks=self.chunks, zarr_data=zarr_data)
                elif lib_name == "OME Zarr":
                    total_time = writer.write_zarr(chunks=self.chunks, zarr_data=zarr_data)
                elif lib_name == "Cpp Zarr":
                    total_time = writer.write_zarr(shape=new_shape, chunks=self.chunks)
                
                # prints info to the terminal 
                print(f"{lib_name} -> creating zarr : {total_time} seconds")
                print(f"The zarr folder is of size {formatted_folder_size(writer.data_path)}\n\n")
                
                write_speeds[lib_name].append((curr_data_size * 10**-9) / total_time) # GB/s
            
            file_sizes.append(curr_data_size * 10**-9) # converts bytes to GB
            multiplier += 4 if multiplier == 1 else 5  # write tests take longer so we increment by 5 
            
        print("--------------------------------------------------------------\n\n")
        
        # plot the data and clean up the folders
        for lib_name, writer in self.__zarr_writers.items():
            # if a specified library is chosen for testing, skip any that isn't that test
            if choose_lib is not None and choose_lib != lib_name: 
                continue 
            
            # cleans up data left behind
            if Path(writer.data_path).exists():
                shutil.rmtree(writer.data_path) 
                
            if graph: 
                graph.plot(file_sizes, write_speeds[lib_name], label=lib_name, marker='o')
            if avg_graph: 
                avg_graph.bar(lib_name, np.average(write_speeds[lib_name]))
            self.__average_bandwidth[lib_name + " Write"] = np.average(write_speeds[lib_name])
              
        if show_results:
            self.__print_results(additional_info=(f"Write Test GB Soft Cap: {num_of_gigabytes}GB"))
            

    def run_append_tests(self, num_of_gigabytes: int, show_results: bool,
                        choose_lib: Optional[str] = None,
                        graph: Optional[matplotlib.axes._axes.Axes] = None, 
                        avg_graph: Optional[matplotlib.axes._axes.Axes] = None) -> None:
        
        # error checking to see if chosen lib exists in test
        if choose_lib is not None and choose_lib not in set(self.__zarr_writers.keys()):
            raise ValueError(f"There is no library of name \"{choose_lib}\".") 
        
        # these are the only libraries that allow for appending of data
        if choose_lib is not None and choose_lib != "TensorStore" and choose_lib != "Zarr Python":
            return
        
        gb_in_bytes = 1073741824         # represents number of bytes in a GB
        write_size = np.prod(self.shape) # amount of bytes appended on in each function call
        multiplier = 1                   # multiplier that increases shape of zarr folder written
        curr_data_size = 0               # test will run until curr_data_size reaches specified GB size passed into the function
        write_speeds = defaultdict(list) # dict that holds the write speeds for every lib tested
        write_numbers = []               # keeps track of writes in list for graphing purposes
        
        print(f"\n\n--------Append Stress Test--------\n\n")
        
        while curr_data_size < (num_of_gigabytes * gb_in_bytes):
            # modify the append dimension, unpack the rest 
            new_shape = [self.shape[0] * (multiplier), *self.shape[1:]]
            
            # 3d array filled with 1 byte ints so multiplication gives accurate size in bytes
            curr_data_size = np.prod(new_shape) 
            
            # creating new data and adjusting the shape
            zarr_data = np.random.randint(low=0, high=256, size=self.shape, dtype=np.uint8)
            
            print("--------------------------------------------------------------------")
            print(f"Current shape : {new_shape} | Current multiplier {multiplier}x")
            print("--------------------------------------------------------------------")
            
            for lib_name, writer in self.__zarr_writers.items():    
                # if a specified library is chosen for testing, skip any that isn't that test
                if choose_lib is not None and choose_lib != lib_name: 
                    continue 
                
                # store time taken to append data
                if lib_name == "TensorStore":
                    total_time = writer.append_zarr(shape=self.shape, chunks=self.chunks, new_shape=new_shape, zarr_data=zarr_data, multiplier=multiplier)
                elif lib_name == "Zarr Python":
                    total_time = writer.append_zarr(shape=self.shape, chunks=self.chunks, zarr_data=zarr_data)
 
                # prints info to the terminal 
                print(f"{lib_name} -> appending zarr : {total_time} seconds")
                print(f"The zarr folder is of size {formatted_folder_size(writer.data_path)}\n\n")
                
                write_speeds[lib_name].append((write_size * 10**-9) / total_time) # GB/s
        
            write_numbers.append(multiplier) # keeps track of the number of writes done by each lib
            multiplier += 1
            
        print("--------------------------------------------------------------\n\n")
            
        # plot the data collected 
        for lib_name, writer in self.__zarr_writers.items():
            # these are the only libraries that allow for appending of data
            if lib_name != "TensorStore" and lib_name != "Zarr Python":
                continue
            
            # if a specified library is chosen for testing, skip any that isn't that test
            if choose_lib is not None and choose_lib != lib_name: 
                continue 
            
            shutil.rmtree(writer.data_path) 
                
            if graph: 
                graph.plot(write_numbers, write_speeds[lib_name], label=lib_name)
            if avg_graph: 
                avg_graph.bar(lib_name, np.average(write_speeds[lib_name]))
            self.__average_bandwidth[lib_name + " Append"] = np.average(write_speeds[lib_name])
              
        if show_results:
            self.__print_results(additional_info=(f"Append Test GB Soft Cap: {num_of_gigabytes}GB"))
    
    
    def run_all_tests(self, append_test_gigabytes: int, write_test_gigabytes: int, 
                      choose_lib: Optional[str] = None,
                      append_graph: Optional[matplotlib.axes._axes.Axes] = None, append_avg_graph: Optional[matplotlib.axes._axes.Axes] = None,
                      write_graph: Optional[matplotlib.axes._axes.Axes] = None, write_avg_graph: Optional[matplotlib.axes._axes.Axes] = None) -> None:
        
        self.run_write_tests(num_of_gigabytes=write_test_gigabytes, show_results=False, choose_lib=choose_lib, graph=write_graph, avg_graph=write_avg_graph)
        self.run_append_tests(num_of_gigabytes=append_test_gigabytes, show_results=False, choose_lib=choose_lib, graph=append_graph, avg_graph=append_avg_graph)
        self.__print_results(additional_info=(f"Write Test GB Soft Cap: {write_test_gigabytes}GB | Append Test GB Soft Cap: {append_test_gigabytes}GB"))
    