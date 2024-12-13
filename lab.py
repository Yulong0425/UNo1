from transformers import AutoModelForQuestionAnswering,  AutoTokenizer, pipeline

model_name = "srcocotero/tiny-bert-qa"

model = AutoModelForQuestionAnswering.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

qa_engine = pipeline('question-answering', model=model, tokenizer=tokenizer)
QA_input = {
    'question': '谁是社管？',
    'context': 'A: 踩刹车的是什么成分不用我多说了吧。B回复:社管|。C回复:死妈社管。D回复:@系噶吃 @爱芙爱芙 社管封杀一下。'}
res = qa_engine (QA_input)

print(res)