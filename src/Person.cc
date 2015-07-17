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
// File: Person.cc
//

#include "Person.h"

#include "Activities.h"
#include "Demographics.h"
#include "Disease_List.h"
#include "Global.h"
#include "Health.h"
#include "Behavior.h"
#include "Place.h"
#include "Disease.h"
#include "Population.h"
#include "Age_Map.h"
#include "Transmission.h"

#include <cstdio>
#include <vector>
#include <sstream>

Person::Person() {
  this->id = -1;
  this->index = -1;
  this->exposed_household_index = -1;
}

Person::~Person() {
}

void Person::setup(int _index, int _id, int age, char sex,
       int race, int rel, Place* house, Place* school, Place* work,
       int day, bool today_is_birthday) {
  int myFIPS;
  this->index = _index;
  this->id = _id;
  this->demographics.setup(this, age, sex, race, rel, day, today_is_birthday);
  this->health.setup(this);
  this->activities.setup(this, house, school, work);
  // behavior setup called externally, after entire population is available

  myFIPS = house->get_household_fips();
  if(today_is_birthday) {
    FRED_VERBOSE(1, "Baby index %d id %d age %d born on day %d household = %s  new_size %d orig_size %d\n",
		 _index, this->id, age, day, house->get_label(), house->get_size(), house->get_orig_size());
  } else {
    // residual immunity does NOT apply to newborns
    for(int disease = 0; disease < Global::Dis.get_number_of_diseases(); ++disease) {
      Disease* dis = Global::Dis.get_disease(disease);
      
      if(Global::Residual_Immunity_by_FIPS) {
  		Age_Map* temp_map = new Age_Map();
  		vector<double> temp_ages = dis->get_residual_immunity()->get_ages();
  		vector<double> temp_values = dis->get_residual_immunity_values_by_FIPS(myFIPS);
  		temp_map->set_ages(temp_ages);
  		temp_map->set_values(temp_values);
     	double residual_immunity_by_fips_prob = temp_map->find_value(this->get_real_age());
	    if(Random::draw_random() < residual_immunity_by_fips_prob) 
	      become_immune(dis);
  		} else if(!dis->get_residual_immunity()->is_empty()) {
	      double residual_immunity_prob = dis->get_residual_immunity()->find_value(this->get_real_age());
	      if(Random::draw_random() < residual_immunity_prob) {
	        become_immune(dis);
	      }
	    }
	  }
  }
}

void Person::print(FILE* fp, int disease) {
  if(fp == NULL) {
    return;
  }
  fprintf(fp, "%d id %7d  a %3d  s %c %d",
          disease, id,
          this->demographics.get_age(),
          this->demographics.get_sex(),
          this->demographics.get_race());
  fprintf(fp, "exp: %2d  inf: %2d  rem: %2d ",
          this->health.get_exposure_date(disease),
          this->health.get_infectious_date(disease),
          this->health.get_recovered_date(disease));
  fprintf(fp, "sympt: %d ", this->health.get_symptomatic_date(disease));
  fprintf(fp, "places %d ", Activity_index::FAVORITE_PLACES);
  fprintf(fp, "infected_at %c %6d ",
          this->health.get_infected_place_type(disease),
          this->health.get_infected_place_id(disease));
  Person* infector = this->health.get_infector(disease);
  int infector_id;
  if(infector == NULL) {
    infector_id = -1;
  } else {
    infector_id = infector->get_id();
  }
  fprintf(fp, "infector %d ", infector_id);
  fprintf(fp, "infectees %d ", this->health.get_infectees(disease));
  fprintf(fp, "antivirals: %2d ", this->health.get_number_av_taken());
  for(int i=0; i < this->health.get_number_av_taken(); ++i) {
    fprintf(fp," %2d", this->health.get_av_start_day(i));
  }
  fprintf(fp,"\n");
  fflush(fp);
}

void Person::become_immune(Disease* disease) {
  int disease_id = disease->get_id();
  if(this->health.is_susceptible(disease_id)) {
    this->health.become_immune(this, disease);
  }
}

void Person::infect(Person* infectee, int disease, Transmission &transmission) {
  this->health.infect(this, infectee, disease, transmission);
}

Person* Person::give_birth(int day) {
  int age = 0;
  char sex = (Random::draw_random(0.0, 1.0) < 0.5 ? 'M' : 'F');
  int race = get_race();
  int rel = Global::CHILD;
  Place* house = this->get_household();
  if(house == NULL) {
    if(Global::Enable_Hospitals && this->is_hospitalized() && this->get_permanent_household() != NULL) {
      house = this->get_permanent_household();
    }
  }
  /*
  if (house == NULL) {
    printf("Mom %d has no household\n", this->get_id()); fflush(stdout);
  }
  */
  assert(house != NULL);
  Place* school = NULL;
  Place* work = NULL;
  bool today_is_birthday = true;
  Person* baby = Global::Pop.add_person(age, sex, race, rel,
                   house, school, work, day, today_is_birthday);

  if(Global::Enable_Behaviors) {
    // turn mother into an adult decision maker, if not already
    if(this->is_health_decision_maker() == false) {
      FRED_VERBOSE(0,
		   "young mother %d age %d becomes baby's health decision maker on day %d\n",
		   id, age, day);
      this->become_health_decision_maker(this);
    }
    // let mother decide health behaviors for child
    baby->set_health_decision_maker(this);
  }
  this->demographics.update_birth_stats(day, this);
  FRED_VERBOSE(1, "mother %d baby %d\n", this->get_id(), baby->get_id());

  return baby;
}

string Person::to_string() {

  stringstream tmp_string_stream;
  // (i.e *ID* Age Sex Race Household School Classroom Workplace Office Neighborhood Hospital Ad_Hoc Relationship)
  tmp_string_stream << this->id << " " << get_age() << " " <<  get_sex() << " " ;
  tmp_string_stream << get_race() << " " ;
  tmp_string_stream << Place::get_place_label(get_household()) << " ";
  tmp_string_stream << Place::get_place_label(get_school()) << " ";
  tmp_string_stream << Place::get_place_label(get_classroom()) << " ";
  tmp_string_stream << Place::get_place_label(get_workplace()) << " ";
  tmp_string_stream << Place::get_place_label(get_office()) << " ";
  tmp_string_stream << Place::get_place_label(get_neighborhood()) << " ";
  tmp_string_stream << Place::get_place_label(get_hospital()) << " ";
  tmp_string_stream << Place::get_place_label(get_ad_hoc()) << " ";
  tmp_string_stream << get_relationship();

  return tmp_string_stream.str();
}

void Person::terminate() {
  FRED_VERBOSE(1, "terminating person %d\n", id);
  this->behavior.terminate(this);
  this->activities.terminate(this);
  this->health.terminate(this);
  this->demographics.terminate(this);
}

