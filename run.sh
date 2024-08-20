PS3="Select an option: "

select opt in experiments paper quit
do
    case ${opt} in
        experiments)
            run_experiments ;
            break;;
        paper)
            build_paper ;
            break;;
        quit)
            break;;
        *)
            echo "invalid option ${REPLY}";;
    esac
done

function run_experiments {
    currdir=$(pwd)
    cd /home/user/experiments
    python runall.py
    cd ${currdir}
} 

function build_paper {
    currdir=$(pwd)
    cd /home/user/paper/figures/py
    python ck_surfaces.py
    cd /home/user/paper
    make figures
    make 
    cd ${currdir}
}
