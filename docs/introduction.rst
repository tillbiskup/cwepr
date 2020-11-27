============
Introduction
============

The truly time-consuming step in nearly every type of spectroscopy is usually *not* data acquisition, but data processing and analysis. However, it seems like in EPR spectroscopy, still every group uses their own routines, and far too often, every student again develops her or his routines again from scratch, reinventing the wheel many times over.

In order to stop this and to allow EPR spectroscopists to focus on actually analysing data and addressing those questions that led to recording EPR spectra in the first place, the cwepr package has been developed.

Besides relieving the cw-EPR spectroscopist from having to write own programs for routine tasks again and again, the cwepr package ensures full reproducibility. This is achieved by being based on the `ASpecD framework <https://docs.aspecd.de/>`_.


"Batteries included" vs. doing everything yourself (again)
==========================================================

Sometimes, people argue against using packages that come with "batteries included" and in favour of writing your own processing and analysis routines from scratch, sometimes for each recorded dataset individually, by claiming that otherwise, people will not get a decent understanding of how to properly process and analyse their data. In addition, using packages would hide the real steps from the operator.

While there is certainly some truth in the statement that people tend to use tools they never understood to an extend that they know not only their potential, but as well their limitations, reinventing the wheel over and over again will not work either, for at least two reasons.

Only a minority of scientists working in the field of EPR spectroscopy have acquired the necessary programming skills to write advanced processing and analysis software by themselves that is sufficiently reliable to ensure correct results.

Additionally, if you always have to start from a blank slate usually you will not come very far, as your day has only 24 hours as well. Meaning: There is good reason why Newton said that his "seeing further" was due to "standing on the shoulder of giants". You better built on top of the solid ground othery laid before you, if you ever want to get somewhere.

Of course, if your only interest is in training other people how to do the first steps, you are free to do so, but in this case, the cwepr package is most probably not the right thing for you. And most probably, neither you nor the people you train will get actual science done in your group.


Batteries included
==================

The idea behind the cwepr package is to provide the cw-EPR spectroscopist with everything they need for processing and analysing their spectra, and this by rather simple means not requiring a major in computing science.

Therefore, many aspects of reproducibility, while being fully transparent, will be taken care of by relying on the `ASpecD framework <https://docs.aspecd.de/>`_. Besides that, recipe-driven data analysis allows the user to perform even complex processing and analysis tasks on several datasets at once without needing to code.

Of course, science often requires us to tackle new and unforeseen questions. However, often this can be achieved by combining existing building blocks. To be honest, only very exceptional scientists are truly able to come up with *original* solutions. Therefore the cwepr package strives for providing its users with an as complete as possible set of basic building blocks for data processing and analysis. Of course, there is always room for improvement, and the package is actively developed by people in the field. Besides that, it is open source and issued under a very permissive license, allowing you to create your own tools based on the existing functionality if needed.


Automate, automate, automate
============================

Another aspect quite central to the cwepr package: Automate whatever processing and analysis step you can automate. This relieves the spectroscopist from having to deal with repetitive, boring and often error-prone tasks if performed manually. Instead, you can focus on the truly important aspects, *i.e.* trying to make sense of the results of your analysis in light of the information available and in context of the original question you tried to address and answer by performing cw-EPR experiments.

Automation includes such routine tasks as analysing power and modulation amplitude sweeps or simply getting an overview of the last batch of samples you've measured. It relies heavily on the report capabilities resulting in well-formatted reports of even complex analyses. For a few more details on reports, you may have a look at the :doc:`concepts <concepts>` section, and for power and modulation amplitude sweeps at the :doc:`cw-EPR primer <cwepr/recording>`.

