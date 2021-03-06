set(libxml2_srcs
    SAX.c entities.c encoding.c error.c parserInternals.c
    parser.c tree.c hash.c list.c xmlIO.c xmlmemory.c uri.c
    valid.c xlink.c HTMLparser.c HTMLtree.c debugXML.c xpath.c
    xpointer.c xinclude.c nanohttp.c nanoftp.c
    catalog.c globals.c threads.c c14n.c xmlstring.c buf.c
    xmlregexp.c xmlschemas.c xmlschemastypes.c xmlunicode.c
    xmlreader.c relaxng.c dict.c SAX2.c
    xmlwriter.c legacy.c chvalid.c pattern.c xmlsave.c
    xmlmodule.c schematron.c xzlib.c)
list(TRANSFORM libxml2_srcs PREPEND ${3RDPARTY}/libxml2/)

add_library(libxml2 STATIC ${libxml2_srcs})
target_include_directories(libxml2 PRIVATE ${3RDPARTY}/libxml2/include)
target_compile_definitions(libxml2 PRIVATE LIBXML_STATIC)
set_target_properties(libxml2 PROPERTIES PREFIX "")

install(FILES ${3RDPARTY}/libxml2/Copyright DESTINATION ${CMAKE_INSTALL_PREFIX}/copyright RENAME COPYING.libxml2)
