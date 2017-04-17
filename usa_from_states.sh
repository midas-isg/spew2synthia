#!/usr/bin/env bash

combine() {
    path=$1
    type=$2

    prefix=spew_1.2.0_usa
    outputPath=${path}/${prefix}
    output=${outputPath}/${prefix}_${type}.txt
    state=2010_ver1_??

    if [ ! -d "$outputPath" ]; then
        mkdir ${outputPath}
    fi

    echo "wrting $output"
    firsTime=true
    for file in ${path}/${state}/*${type}.txt
    do
        if "${firsTime}" == "true"; then
            head -n1 ${file} > ${output}
            firsTime="false"
        fi
        echo "   reading ${file}"
        tail -n+2 ${file} >> $output
    done
    #echo ${output}
}

path=./populations
combine $path schools
combine $path synth_gq
combine $path synth_gq_people
combine $path synth_households
combine $path synth_people
combine $path workplaces
echo DONE!