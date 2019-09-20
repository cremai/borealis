**********************
Building an Experiment
**********************

Borealis has an extensive set of features and this means that experiments can end up having lots of functionality and complicated functions. To help organize writing of experiments, we've designed the system so that experiments can be broken into smaller components, called slices, that interface together with other components to perform desired functionality. An experiment can have a single slice or several working together, depending on the complexity.

Each slice contains the information needed about a specific pulse sequence to run. The parameters of a slice contain features such as pulse sequence, frequency, fundamental time lag spacing, etc. These are the parameters that researchers will be familiar with.

The other necessary part of an experiment is specifying how slices will interface with each other. Interfacing in this case refers to how these two components are meant to be run. The following types of interfacing are possible:

1. SCAN. The scan by scan interfacing allows for slices to run a scan of one slice, followed by a scan of the second. The scan mode of interfacing typically means that the slice will cycle through all of its beams before switching to another slice.
2. INTTIME. This type of interfacing allows for an integration period to run for one slice, before switching to another. This type of interface effectively creates an interleaving scan where the scans for different slices are run simultaneously, however the pulse sequences are alternated rather than run concurrently.
3. INTEGRATION. Integration interfacing allows for pulse sequences defined in the slices to alternate between each other within an integration period. Slices which are interfaced in this manner must share the same INTT and INTN values for this to work.
4. PULSE. Pulse interfacing allows for pulse sequences to be run together concurrently. Slices will have their pulse sequences mixed and layered together so that the data transmits at the same time. Slices of different frequencies can be mixed simultaneously and slices of different pulse sequences can also run together at the cost of having more blanked samples.

Writing an Experiment
---------------------

All experiments must be written as their own class and must be built off of the built-in ExperimentPrototype class.  This means the ExperimentPrototype class must be imported
at the start of the experiment file::

    from experiments.experiment_prototype import ExperimentPrototype

You must also build your class off of the ExperimentPrototype class, which involves inheritance. To do this, define your class
like so::

    class MyClass(ExperimentPrototype):

        def __init__(self):
            cpid = 123123  # this must be a unique id for your control program.
            super(MyClass, self).__init__(cpid)

The experiment handler will create an instance of your experiment when your experiment is scheduled to start running. Your class is a child class of ExperimentPrototype and because of this, the parent class needs to be instantiated when the experiment is instantiated. This is important because the experiment_handler will build the scans required by your class in a way that is easily readable and iterable by the radar control program. This is done by methods that are set up in the ExperimentPrototype parent class.

The next step is to add slices to your experiment. An experiment is defined by the slices in the class, and how the slices interface.


TODO

..  TODO outline ways to interface

..  TODO determine where users should write their experiments
    because that will affect the import statement - putting them
    directly in experiments?

Checking your Experiment for Errors
-----------------------------------

..  TODO how to check your experiment for errors
