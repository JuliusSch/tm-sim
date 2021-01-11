# Turing Machine Simulator
This program offers a visual representation of Alan Turing's *a-machine*, which can be understood as the most stripped-down, simple computer imaginable. His major work was to prove that the set of operations capable on **any** computer is no greater than the set of operations capable on such a simple machine. In other words, computer speed and complexity (including such things as the presence of RAM and other modern components) have no bearing on what kind of operations are computable on the machine (in a theoretical sense, speed is obviously a practical concern). The inverse holds also. If the Turing machine is incapable of running a function, so is every computer. From this, Turing constructed a theory of the limits of standard computing. This is commonly called the Halting Problem, which details the impossibility of a program which computes whether other programs will succeed or run forever. For more reading see [here](https://en.wikipedia.org/wiki/Halting_problem).
 The program supports editing the tape, pausing and starting the machine, tracking which instruction is currently being executed and variable running speeds for quick calculation or slow analysis of the steps. Additionally, for those who want to write their own Turing machine for the program to run, this can be done by adding a folder with the name of the machine and adding text files for alphabet, initial tape, states and instructions in the same manner as the included programs.

## Demo

![A program running](demo/turing-machine-running.gif)

The machine is shown here completing one operation, namely the adding of two binary numbers.
