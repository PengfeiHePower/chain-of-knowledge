export TRANSFORMERS_VERBOSITY=error
export CUDA_VISIBLE_DEVICES=0
CUDA_VISIBLE_DEVICES=1 python run.py --model qwen --dataset hotpotqa --output outputs/hotpotqa/qwen_hotpotqa_output.json  --step True --num_test 100
CUDA_VISIBLE_DEVICES=1 python run.py --model gpt-4 --dataset medmcqa --output outputs/medmcqa/medmcqa_output.json  --step True --num_test 146 --threshold 0.8 
CUDA_VISIBLE_DEVICES=1 python run.py --model gpt-4 --dataset mmluphy --output outputs/mmluphy/mmluphy_output.json  --step True --num_test 100 --threshold 0.8
CUDA_VISIBLE_DEVICES=1 python run.py --model gpt-4 --dataset mmlubio --output outputs/mmlubio/mmlubio_output.json  --step True --num_test 100 --threshold 0.8
CUDA_VISIBLE_DEVICES=1 python run.py --model gpt-4 --dataset fever --output outputs/fever/fever_output.json  --step True --num_test 100
# gpt-3.5-turbo-0613