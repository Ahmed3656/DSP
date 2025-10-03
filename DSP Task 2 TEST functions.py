#!/usr/bin/env python
# coding: utf-8
# %%

# %%

from signal_app.signals import Signal

def ReadSignalFile(file_name):
    expected_indices=[]
    expected_samples=[]
    with open(file_name, 'r') as f:
        line = f.readline()
        line = f.readline()
        line = f.readline()
        line = f.readline()
        while line:
            # process line
            L=line.strip()
            if len(L.split(' '))==2:
                L=line.split(' ')
                V1=int(L[0])
                V2=float(L[1])
                expected_indices.append(V1)
                expected_samples.append(V2)
                line = f.readline()
            else:
                break
    return expected_indices,expected_samples


# %%


def AddSignalSamplesAreEqual(userFirstSignal,userSecondSignal,Your_indices,Your_samples):
    if(userFirstSignal=='Signal1.txt' and userSecondSignal=='Signal2.txt'):
        file_name="add.txt"  # write here the path of the add output file
    expected_indices,expected_samples=ReadSignalFile(file_name)          
    if (len(expected_samples)!=len(Your_samples)) and (len(expected_indices)!=len(Your_indices)):
        print("Addition Test case failed, your signal have different length from the expected one")
        return
    for i in range(len(Your_indices)):
        if(Your_indices[i]!=expected_indices[i]):
            print("Addition Test case failed, your signal have different indicies from the expected one") 
            return
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Addition Test case failed, your signal have different values from the expected one") 
            return
    print("Addition Test case passed successfully")

# First, load your input signals from file
sig1 = Signal.from_txt_file("Signal1.txt", name="original")
sig2 = Signal.from_txt_file("Signal2.txt", name="original")

# add them
add_sig = sig1.add(sig2, name="add")

# Convert to sorted indices & samples
indices, samples = add_sig.to_sorted_series()

# Run the provided test function
AddSignalSamplesAreEqual("Signal1.txt", "Signal2.txt",indices,samples)


# %%

def SubSignalSamplesAreEqual(userFirstSignal,userSecondSignal,Your_indices,Your_samples):
    if(userFirstSignal=='Signal1.txt' and userSecondSignal=='Signal2.txt'):
        file_name="subtract.txt" # write here the path of the subtract output file
        
    expected_indices,expected_samples=ReadSignalFile(file_name)   
    
    if (len(expected_samples)!=len(Your_samples)) and (len(expected_indices)!=len(Your_indices)):
        print("Subtraction Test case failed, your signal have different length from the expected one")
        return
    for i in range(len(Your_indices)):
        if(Your_indices[i]!=expected_indices[i]):
            print("Subtraction Test case failed, your signal have different indicies from the expected one") 
            return
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Subtraction Test case failed, your signal have different values from the expected one") 
            return
    print("Subtraction Test case passed successfully")
    

# First, load your input signals from file
sig1 = Signal.from_txt_file("Signal1.txt", name="original")
sig2 = Signal.from_txt_file("Signal2.txt", name="original")

# subtract them
sub_sig = sig1.subtract(sig2, name="subtract")

# Convert to sorted indices & samples
indices, samples = sub_sig.to_sorted_series()

# Run the provided test function
SubSignalSamplesAreEqual("Signal1.txt", "Signal2.txt",indices,samples)  # call this function with your computed indicies and samples


# %%


def MultiplySignalByConst(User_Const,Your_indices,Your_samples):
    if(User_Const==5):
        file_name="mul5.txt"  # write here the path of the mul5 output file
        
    expected_indices,expected_samples=ReadSignalFile(file_name)      
    if (len(expected_samples)!=len(Your_samples)) and (len(expected_indices)!=len(Your_indices)):
        print("Multiply by "+str(User_Const)+ " Test case failed, your signal have different length from the expected one")
        return
    for i in range(len(Your_indices)):
        if(Your_indices[i]!=expected_indices[i]):
            print("Multiply by "+str(User_Const)+" Test case failed, your signal have different indicies from the expected one") 
            return
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Multiply by "+str(User_Const)+" Test case failed, your signal have different values from the expected one") 
            return
    print("Multiply by "+str(User_Const)+" Test case passed successfully")

# First, load your input signal from file
sig = Signal.from_txt_file("Signal1.txt", name="original")

# Multiply it by 5
mul_sig = sig.multiply(5, name="mul5")

# Convert to sorted indices & samples
indices, samples = mul_sig.to_sorted_series()

# Run the provided test function
MultiplySignalByConst(5, indices, samples)


# %%


def ShiftSignalByConst(Shift_value,Your_indices,Your_samples):
    if(Shift_value==3):  #x(n+k)
        file_name="delay3.txt" # write here the path of delay3 output file
    elif(Shift_value==-3): #x(n-k)
        file_name="advance3.txt" # write here the path of advance3 output file

    expected_indices,expected_samples=ReadSignalFile(file_name)
    if (len(expected_samples)!=len(Your_samples)) and (len(expected_indices)!=len(Your_indices)):
        print("Shift by "+str(Shift_value)+" Test case failed, your signal have different length from the expected one")
        return
    for i in range(len(Your_indices)):
        if(Your_indices[i]!=expected_indices[i]):
            print("Shift by "+str(Shift_value)+" Test case failed, your signal have different indicies from the expected one") 
            return
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Shift by "+str(Shift_value)+" Test case failed, your signal have different values from the expected one") 
            return
    print("Shift by "+str(Shift_value)+" Test case passed successfully")


# First, load your input signal from file
sig = Signal.from_txt_file("Signal1.txt", name="original")
# Shift it by 3
ShiftSignal_value = 3  # Change this to -3 to test the other case
shift_sig = sig.shift(ShiftSignal_value, name="shifted")
# Convert to sorted indices & samples
indices, samples = shift_sig.to_sorted_series()
# Run the provided test function
ShiftSignalByConst(ShiftSignal_value,indices,samples)  # call this function with your computed indicies and samples

# %%


def Folding(Your_indices,Your_samples):
    file_name = "folding.txt"  # write here the path of the folding output file
    expected_indices,expected_samples=ReadSignalFile(file_name)      
    if (len(expected_samples)!=len(Your_samples)) and (len(expected_indices)!=len(Your_indices)):
        print("Folding Test case failed, your signal have different length from the expected one")
        return
    for i in range(len(Your_indices)):
        if(Your_indices[i]!=expected_indices[i]):
            print("Folding Test case failed, your signal have different indicies from the expected one") 
            return
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Folding Test case failed, your signal have different values from the expected one") 
            return
    print("Folding Test case passed successfully")

# First, load your input signal from file
sig = Signal.from_txt_file("Signal1.txt", name="original")
# Fold it
fold_sig = sig.fold(name="folded")
# Convert to sorted indices & samples
indices, samples = fold_sig.to_sorted_series()
# Run the provided test function
Folding(indices,samples)  # call this function with your computed indicies and samples

# %%
