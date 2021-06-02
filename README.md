# Language-annotated Abstraction and Reasoning Corpus (LARC)

This repository contains the language annotated data with supporting assets for LARC, as discussed in [Communicating Natural Programs to Humans and Machines](link todo)

"LARC is a collection of natural language descriptions by a group of human participants, unfamiliar both with ARC and with each other, who instruct each other on how to solve ARC tasks."

The original ARC data can be found here [The Abstraction and Reasoning Corpus github](https://github.com/fchollet/ARC)

Annotations in LARC takes the form of a communication game, where 
one participant, the *describer* solves an ARC task and describes the underlying rules using language to a different participant, 
the *builder*, who must solve the task on the new input using the description alone. 

<style type="text/css">
img[src~="thumbnail"] {
   border: 4px solid gray;
}
</style>

![collection process](https://raw.githubusercontent.com/samacqua/LARC/main/assets/collection.jpg#thumbnail)


The entire dataset can be browsed at [the explorer interface](link todo)

Citation
```
@inproceedings{Larky Larc,
}
```

## Contents
- `dataset` contains the language-annotated ARC tasks and successful natural program phrase annotations
- `explorer` contains the explorer code that allows for easy browsing of the annotated tasks
- `collection` contains the source code used to curate the dataset
- `bandit` contains the formulation and environment for bandit algorithm used for collection
