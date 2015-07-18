/*
  This file is part of the FRED system.

  Copyright (c) 2010-2015, University of Pittsburgh, John Grefenstette,
  Shawn Brown, Roni Rosenfield, Alona Fyshe, David Galloway, Nathan
  Stone, Jay DePasse, Anuroop Sriram, and Donald Burke.

  Licensed under the BSD 3-Clause license.  See the file "LICENSE" for
  more information.
*/

//
//
// File: Disease_List.h
//

#ifndef _FRED_DISEASE_LIST_H
#define _FRED_DISEASE_LIST_H

#include <vector>
#include <string>
using namespace std;

class Disease;


class Disease_List {

public:
  Disease_List() {};
  ~Disease_List() {};
  void get_parameters(int num_of_diseases);
  void setup();
  Disease* get_disease(int disease_id) {
    return diseases[disease_id];
  }
  int get_number_of_diseases() { 
    return this->number_of_diseases;
  }

 private:
  std::vector <Disease*> diseases;
  int number_of_diseases;
  string * disease_name;
};

#endif // _FRED_DISEASE_LIST_H
