class Category():

    def __init__(self, id: int, name: str,):
        self.id = id
        self.name = name

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    def __str__(self):
        return "{}: {}".format(self.id, self.name)
    

class QuestionsAnswers():

    def __init__(self, id:int, question:str, ans:str, w1:str, w2:str, category_id=None):
        self.id = id
        self.question = question
        self.ans = ans
        self.w1 = w1
        self.w2 = w2
        self.category_id = category_id

    def serialize(self):
        return {
            'id': self.id,
            'question': self.question,
            'ans': self.ans,
            'w1': self.w1,
            'w2': self.w2,
            'category_id': self.category_id,
        }

    def __str__(self):
        return "PREGUNTA: {}".format(self.question)
