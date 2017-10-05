PROGS= norm 
SM=
norm: norm.cu
	nvcc -o $@ $^ $(SM)

clean:
	rm $(PROGS)
