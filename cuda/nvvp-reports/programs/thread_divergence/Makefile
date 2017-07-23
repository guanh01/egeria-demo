NVCC=nvcc -w -arch=sm_35 -std=c++11 -lcublas -O3 -Xcompiler -fopenmp 
all: knnjoin knnjoin_opt
knnjoin: knnjoin.cu
	$(NVCC) -o $@ $^  

knnjoin_opt: knnjoin_opt.cu
	$(NVCC) -o $@ $^

clean: rm knnjoin 
