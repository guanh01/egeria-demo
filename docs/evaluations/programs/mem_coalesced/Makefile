NVCC=nvcc -w -arch=sm_35 
all: trans trans_opt
trans: trans.cu
	$(NVCC) -o $@ $^

trans_opt: trans_opt.cu
	$(NVCC) -o $@ $^
clean:
	rm trans trans_opt
