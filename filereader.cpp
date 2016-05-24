#include <vector>
#include <map>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>

class filereader {
private:
  std::ifstream in_file;
  int layer;
  int color;
  float thickness;

public:
  std::map <std::string, std::vector < std::vector < float > > > positions;
  std::map <std::string, std::vector < float > > thicknesses;
  std::map <std::string, std::vector < int > > colors;
  std::map <std::string, std::vector < int > > layers;
  std::map <std::string, std::vector < std::string > > texts;

  filereader(std::string fname){
    in_file.open(fname.c_str(), std::ifstream::in);
  };
  ~filereader(){
    in_file.close();
  };

  std::vector<float> fetch(std::istringstream &sline, unsigned int size){
    std::vector < float > read_vec (size);
    for(unsigned int i=0; i<size; i++){
      sline >> read_vec[i];
    }
    return read_vec;
  };

  void getCircle(std::istringstream &sline) {;
    positions["c"].push_back(fetch(sline, 3));
    thicknesses["c"].push_back(thickness);
    colors["c"].push_back(color);
    layers["c"].push_back(layer);
  };

  void getLine(std::istringstream &sline) {;
    positions["l"].push_back(fetch(sline, 6));
    colors["l"].push_back(color);
    layers["l"].push_back(layer);
  };

  void getString(std::istringstream &sline) {;
    positions["s"].push_back(fetch(sline, 6));
    thicknesses["s"].push_back(thickness);
    colors["s"].push_back(color);
    layers["s"].push_back(layer);
  };

  void getText(std::istringstream &sline) {;
    positions["t"].push_back(fetch(sline, 3));
    colors["t"].push_back(color);
    layers["t"].push_back(layer);
    std::string t;
    std::getline(sline, t);
    texts["t"].push_back(t);
  };

  bool get(){
    std::string cmd;
    positions.clear();
    colors.clear();
    layers.clear();
    thicknesses.clear();
    texts.clear();
    bool empty = true;
    for (std::string line; std::getline(in_file, line); ) {
      if (line.empty()) {
        break;
      }
      empty = false;
      std::istringstream sline(line);
      sline >> cmd;
      if (cmd == "c") {
        getCircle(sline);
      } else if (cmd == "s") {
        getString(sline);
      } else if (cmd == "l") {
        getLine(sline);
      } else if (cmd == "t") {
        getText(sline);
      } else if (cmd == "y") {
        sline >> layer;
      } else if (cmd == "@") {
        sline >> color;
      } else if (cmd == "r") {
        sline >> thickness;
      } else {
        std::cout << "[ chochin ] unrecognized command " << line << std::endl;
      }
    }
    return !empty;
  };

};
