data_repo_path=$1

if [ "$#" -ne 1 ]; then
    echo "usage: bash link_data.sh <path to data repo>"
    echo "data repo: git@gitlab.oth-regensburg.de:IM/lfd/dissemination/phd/krueger_tom/cost_function_expectation_paper_data.git"
else
    rp=`realpath ${data_repo_path}`;
    if [[ ! -d "figures/links/" ]]; then mkdir -p "figures/links/"; fi

    ln -s ${rp}/out/uniform figures/links/
    ln -s ${rp}/out/clustered figures/links/
    ln -s ${rp}/out/sat figures/links/
    ln -s ${rp}/out/qrfactoring_approx figures/links/
    ln -s ${rp}/out/uniform_preopt figures/links/
    ln -s ${rp}/out/clustered_preopt figures/links/
    ln -s ${rp}/out/sat_preopt figures/links/
    ln -s ${rp}/out/qrf_preopt figures/links/
fi
