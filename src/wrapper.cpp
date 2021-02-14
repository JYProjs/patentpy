#include "convert_funcs.hpp"
#include <pybind11/pybind11.h>

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

namespace py = pybind11;

PYBIND11_MODULE(convert_funcs, m) {
    m.doc() = "Plugin to convert USPTO txt formatted data to dataframe";

    m.def("txt_to_df", &txt_to_df_cpp, "A function that takes USPTO (1976-2001) data from txt file, extracts pertinent fields, and creates (or appends to) csv output");

#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif
}