from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import *
import jwt
from datetime import datetime, timedelta

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "YOUR_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Укажите домен вашего React-приложения
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)



# Создание OAuth2PasswordBearer для аутентификации
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Проверка JWT токена
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return email

# Маршрут для аутентификации и получения токена


@app.post("/token")
async def login_for_access_token(form_data: LoginForm):
    db = SessionLocal()
    user = db.query(User).filter(User.Email == form_data.Email, User.Password == form_data.Password).first()
    db.close()
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.Email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}



# Обработчик для регистрации нового пользователя
@app.post("/register")
async def register(new_user: NewUser):
    db = SessionLocal()

    # Проверяем, существует ли пользователь с таким email
    user_exists = db.query(User).filter(User.Email == new_user.Email).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

    # Создаем объект пользователя для вставки в базу данных
    user_db = User(Email=new_user.Email, Name=new_user.Name, Password=new_user.Password,
                   Birthday=new_user.Birthday, City=new_user.City, Edu=new_user.Edu,
                   Course=new_user.Course, Group=new_user.Group)

    # Добавляем пользователя в сессию
    db.add(user_db)
    # Подтверждаем изменения и закрываем сессию
    db.commit()
    db.close()
    return {"message": "Пользователь успешно зарегистрирован"},200


@app.post("/login")
async def login(login_data: LoginData):
    db = SessionLocal()

    # Проверяем, существует ли пользователь с указанным email и паролем
    user = db.query(User).filter(User.Email == login_data.Email, User.Password == login_data.Password).first()
    if user:
        # Если пользователь существует, возвращаем его данные
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user.Email}, expires_delta=access_token_expires)
        return {"Email": user.Email, "Name": user.Name, "Password": user.Password, 'Token':access_token}
    else:
        # Если пользователь не найден, возвращаем ошибку HTTP 400
        raise HTTPException(status_code=400, detail="Пользователь с указанным email и паролем не найден")

@app.post("/users/info/simple_no_pass")
async def User_Info_Simple(user: User_info):
    db = SessionLocal()
    # Проверяем, существует ли пользователь с указанным email и паролем
    user = db.query(User).filter(User.Email == user.Email).first()
    if user:
        # Если пользователь существует, возвращаем его данные
        return {"User_ID": user.User_ID, "Email": user.Email, "Name": user.Name}
    else:
        # Если пользователь не найден, возвращаем ошибку HTTP 400
        raise HTTPException(status_code=400, detail="Пользователь с указанным email не найден")

@app.post("/users/info/full_no_password")
async def User_Info_Full(users: User_info):
    db = SessionLocal()
    # Проверяем, существует ли пользователь с указанным email и паролем

    payload = jwt.decode(users.Token, SECRET_KEY, algorithms=[ALGORITHM])
    email: str = payload.get("sub")

    user = db.query(User).filter(User.Email == email).first()
    if user:
        # Если пользователь существует, возвращаем его данные
        return {"Email": user.Email, "Name": user.Name, "Birthday": user.Birthday, "City":user.City, "EDU":user.Edu,"Course":user.Course, "Group":user.Group, "Phone":user.Phone,"Tg":user.Tg, "Discord":user.Discord, "VK":user.VK}
    else:
        # Если пользователь не найден, возвращаем ошибку HTTP 400
        raise HTTPException(status_code=400, detail="Пользователь с указанным email не найден")

@app.post("/users/info/update")
async def update_user(user_update: User_Update):

    payload = jwt.decode(user_update.Token, SECRET_KEY, algorithms=[ALGORITHM])
    email: str = payload.get("sub")

    db = SessionLocal()
    user = db.query(User).filter(User.Email == email).first()
    if user is None:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    user_data = user_update.dict(exclude_unset=True)
    for key, value in user_data.items():
        setattr(user, key, value)
    db.commit()
    db.close()
    return {"message": "Данные пользователя успешно обновлены"}

@app.post("/users/info/delete")
async def user_delete(user_update: User_info):
    db = SessionLocal()
    user = db.query(User).filter(User.Email == user_update.Email).first()
    if user is None:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    db.delete(user)
    db.commit()
    db.close()
    return {"message": "Успешно"}

@app.get("/test/special")
async def get_specials():
    db = SessionLocal()
    # Выполняем запрос к базе данных для получения всех записей из таблицы "Special"
    specials = db.query(Special).all()

    # Преобразуем результаты запроса в список словарей
    special_data = []
    for special in specials:
        special_data.append({"ID_Special": special.ID_Special, "Name": special.Name})

    # Возвращаем данные в формате JSON
    return special_data

@app.post("/test/OTF")
async def get_OTF(sp:Special_OFT):
    db = SessionLocal()
    # Выполняем запрос к базе данных для получения всех записей из таблицы "OTF"
    otfs = db.query(OTF).filter(OTF.ID_Special == sp.ID_Special).all()

    # Проверяем, есть ли записи для указанного ID_Special
    if not otfs:
        raise HTTPException(status_code=404, detail="OTFs not found for the specified ID_Special")

    # Получаем информацию о специальности
    special = otfs[0].special

    # Формируем ответ
    response_data = {
        "ID_Special": special.ID_Special,
        "Special_Name": special.Name,
        "OTFs": []
    }
    for otf in otfs:
        response_data["OTFs"].append({
            "ID_OTF": otf.ID_OTF,
            'Category': otf.Category,
            "OTF_name": otf.Name
        })

    return response_data



@app.post("/get_questions")
async def get_questions(data: RequestData):
    db = SessionLocal()

    # Извлекаем значения ID_Special и OTF_Categories из полученного JSON
    id_special = data.ID_Special
    otf_categories = data.OTF_Categories.split(",")

    # Выполняем запрос к базе данных
    result = db.query(Special.ID_Special, Special.Name, OTF.ID_OTF, OTF.Category, OTF.Name, TF.ID_TF, TF.Name, TD.ID_TD, TD.Name) \
        .join(OTF, Special.ID_Special == OTF.ID_Special) \
        .join(TF, TF.ID_OTF == OTF.ID_OTF) \
        .join(TD, TD.ID_TF == TF.ID_TF) \
        .filter(OTF.Category.in_(otf_categories)) \
        .filter(Special.ID_Special == id_special) \
        .all()

    if not result:
        raise HTTPException(status_code=400, detail="Пусто")

    # Преобразуем результаты запроса в нужный формат
    response_data = {
        "ID_Special": id_special,
        "Special_Name": result[0][1],
        "OTFs": []
    }

    otf_data = {}
    for row in result:
        otf_id = row[2]
        tf_id = row[5]
        if otf_id not in otf_data:
            otf_data[otf_id] = {
                "ID_OTF": otf_id,
                "Category": row[3],
                "OTF_name": row[4],
                "TFs": {}
            }

        if tf_id not in otf_data[otf_id]["TFs"]:
            otf_data[otf_id]["TFs"][tf_id] = {
                "TF_ID": tf_id,
                "TF_Name": row[6],
                "TDs": []
            }

        otf_data[otf_id]["TFs"][tf_id]["TDs"].append({
            "TD_ID": row[7],
            "TD_Name": row[8]
        })

    for otf_id, otf_info in otf_data.items():
        otf_info["TFs"] = list(otf_info["TFs"].values())
        response_data["OTFs"].append(otf_info)

    return response_data

@app.post("/submit_answers")
async def submit_answers(data: dict):
    db = SessionLocal()

    try:

        payload = jwt.decode(data["Token"], SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        # Проверяем, существует ли пользователь с указанным логином
        user = db.query(User).filter(User.Email == email).first()
        if not user:
            raise HTTPException(status_code=400, detail="User not found")

        # Записываем данные в таблицу History
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")
        history_entry = History(User_ID=user.User_ID, DATE=current_date, TIME=current_time)
        db.add(history_entry)
        db.commit()

        # Получаем ID_Pass для новой записи в таблице Pass
        pass_id = history_entry.ID_Pass

        # Записываем ответы пользователя в таблицу Pass и считаем сумму баллов
        for answer in data["ANS"]:
            td = db.query(TD).filter(TD.ID_TD == answer["ID_TD"]).first()
            tf = db.query(TF).filter(TF.ID_TF == td.ID_TF).first()
            otf = db.query(OTF).filter(OTF.ID_OTF == tf.ID_OTF).first()
            pass_entry = Pass(
                ID_Pass=pass_id,
                Special=data["ID_Special"],
                OTF=otf.ID_OTF,
                TF=tf.ID_TF,
                TD=td.ID_TD,
                Score=answer["Answer"]
            )
            db.add(pass_entry)

            # Проверяем, существует ли запись для данного TD в таблице All_Pass
            all_pass_entry = db.query(All_Pass).filter(All_Pass.TD == answer["ID_TD"]).first()
            if all_pass_entry:
                all_pass_entry.Kol_vo += 1
                all_pass_entry.SUMM += answer["Answer"]
                all_pass_entry.Medium = all_pass_entry.SUMM/all_pass_entry.Kol_vo
            else:
                # Находим TF и OTF для данного TD


                # Создаем новую запись для TD
                all_pass_entry = All_Pass(
                    Special=data["ID_Special"],
                    OTF=otf.ID_OTF,
                    TF=tf.ID_TF,
                    TD=td.ID_TD,
                    Kol_vo=1,
                    SUMM=answer["Answer"],
                    Medium= answer["Answer"]/1 # Нужно ли здесь вычислять Medium или он будет вычислен в другом месте?
                )
                db.add(all_pass_entry)

        db.commit()

        return {"message": "Answers submitted successfully", "ID_Pass": pass_id}


    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to submit answers: " + str(e))

    finally:
        db.close()

from typing import List, Union
from sqlalchemy import desc
from sqlalchemy import create_engine, func
from collections import defaultdict
@app.post("/get_last_results")
async def calculate_scores(data: dict):
    db = SessionLocal()

    try:
        payload = jwt.decode(data["Token"], SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        # Получаем пользователя по email
        user = db.query(User).filter(User.Email == email).first()
        if not user:
            raise HTTPException(status_code=400, detail="User not found")

        # Получаем последний пройденный Pass для пользователя
        last_pass = db.query(Pass).join(History, Pass.ID_Pass == History.ID_Pass) \
            .filter(History.User_ID == user.User_ID) \
            .order_by(History.ID_Pass.desc()) \
            .first()
        if not last_pass:
            raise HTTPException(status_code=400, detail="No Pass found for the user")

        # Получаем название специальности
        special_name = db.query(Special.Name).filter(Special.ID_Special == last_pass.Special).first()
        if not special_name:
            raise HTTPException(status_code=400, detail="Special not found")

        # Получаем общее количество ответов
        total_scores_query = db.query(func.count(Pass.ID_Pass)).filter(Pass.ID_Pass == last_pass.ID_Pass).scalar()
        if not total_scores_query:
            raise HTTPException(status_code=400, detail="No scores found for the user")

        total_scores = total_scores_query

        # Формируем запрос для подсчета количества ответов на каждый балл
        query_result = db.query(Pass.Score, func.count(Pass.ID_Pass)).filter(
            Pass.ID_Pass == last_pass.ID_Pass).group_by(Pass.Score).all()

        # Создаем словарь для хранения результатов
        score_percentages = {"A": 0, "B": 0, "C": 0, "D": 0}

        # Преобразуем числовые значения баллов в буквенные
        score_mapping = {1: "A", 2: "B", 3: "C", 4: "D"}

        for score, count in query_result:
            if score in score_mapping:
                score_letter = score_mapping[score]
                score_percentages[score_letter] = (count / total_scores) * 100

        return {
            "Special_Name": special_name[0],
            "Scores_Percentages": score_percentages
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token signature has expired")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate scores percentages: {str(e)}")

    finally:
        db.close()


@app.post("/pass_history")
async def get_pass_history(data: dict):
    db = SessionLocal()

    try:
        payload = jwt.decode(data["Token"], SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        # Получаем историю прохождений пользователя
        user = db.query(User).filter(User.Email == email).first()
        if not user:
            raise HTTPException(status_code=400, detail="User not found")

        pass_history = db.query(History.ID_Pass, History.DATE, History.TIME) \
            .filter(History.User_ID == user.User_ID) \
            .order_by(desc(History.DATE), desc(History.TIME)) \
            .all()

        if not pass_history:
            raise HTTPException(status_code=400, detail="Pass history not found for the user")

        # Формируем результаты
        pass_history_data = []
        for history_entry in pass_history:
            pass_id, date, time = history_entry
            pass_entry = db.query(Pass).filter(Pass.ID_Pass == pass_id).first()
            if pass_entry:
                special_id = pass_entry.Special
                special_name = db.query(Special.Name).filter(Special.ID_Special == special_id).first()
                if special_name:
                    pass_history_data.append({
                        "ID_Pass": pass_id,
                        "Date": date,
                        "Time": time,
                        "Special_ID": special_id,
                        "Special_Name": special_name[0]
                    })

        return pass_history_data

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token signature has expired")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pass history: {str(e)}")

    finally:
        db.close()


@app.post("/otf_spider_diagram")
async def get_otf_spider_diagram(d: dict):
    db = SessionLocal()

    try:
        # Получаем объект прохождения по его ID
        pass_entry = db.query(Pass).filter(Pass.ID_Pass == d["ID_Pass"]).first()
        if not pass_entry:
            raise HTTPException(status_code=404, detail="Pass entry not found")

        # Получаем объект Special, связанный с прохождением
        special_entry = db.query(Special).filter(Special.ID_Special == pass_entry.Special).first()
        if not special_entry:
            raise HTTPException(status_code=404, detail="Special entry not found")

        # Получаем все OTF, связанные с данной специальностью
        otf_entries = db.query(OTF).filter(OTF.ID_Special == special_entry.ID_Special).all()
        if not otf_entries:
            raise HTTPException(status_code=404, detail="OTF entries not found")

        # Получаем запись из истории
        pass_history_entry = db.query(History).filter(History.ID_Pass == d["ID_Pass"]).first()
        if not pass_history_entry:
            raise HTTPException(status_code=404, detail="Pass history entry not found")

        # Собираем данные
        pass_data = {
            "ID_Pass": pass_history_entry.ID_Pass,
            "Special_ID": pass_entry.Special,
            "Special_Name": special_entry.Name,
            "Date": pass_history_entry.DATE,
            "Time": pass_history_entry.TIME,
            "OTFs": []
        }

        for otf_entry in otf_entries:
            # Фильтруем записи Pass по OTF и ID_Pass
            pass_entries = db.query(Pass).filter(Pass.OTF == otf_entry.ID_OTF, Pass.ID_Pass == d["ID_Pass"]).all()
            if pass_entries:
                total_score = sum(entry.Score for entry in pass_entries)
                average_score = round(total_score / len(pass_entries), 1)
            else:
                average_score = 0

            pass_data["OTFs"].append({
                "OTF_Name": otf_entry.Name,
                "Scale": average_score
            })

        return pass_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch OTF spider diagram data: {str(e)}")

    finally:
        db.close()


from sqlalchemy import func

@app.post("/average_scores")
async def get_average_scores_by_special(data: dict):
    db = SessionLocal()

    try:
        # Получаем ID_Special из запроса
        special_id = data.get("ID_Special")

        # Получаем список OTF для данного ID_Special
        otf_list = db.query(OTF).filter(OTF.ID_Special == special_id).all()

        if not otf_list:
            raise HTTPException(status_code=404, detail="No OTF found for the specified Special ID")

        # Создаем пустой список для хранения усредненных значений для каждого OTF
        average_scores = []

        # Для каждого OTF вычисляем усредненное значение из таблицы All_Pass
        for otf in otf_list:
            otf_name = otf.Name
            otf_id = otf.ID_OTF

            # Получаем усредненное значение из таблицы All_Pass для данного OTF
            average_score = db.query(func.avg(All_Pass.Medium)) \
                                .filter(All_Pass.Special == special_id, All_Pass.OTF == otf_id) \
                                .scalar()

            # Добавляем усредненное значение в список
            average_scores.append({
                "OTF_Name": otf_name,
                "Average_Score": round(average_score, 1) if average_score else 0
            })

        return average_scores

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch average scores: {str(e)}")

    finally:
        db.close()

from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any    
score_to_text = {1: 'one', 2: 'two', 3: 'three', 4: 'four'}

@app.post("/get_sorted_answers")
async def get_sorted_answers(data: Dict[str, Any]):
    db: Session = SessionLocal()

    try:
        # Получаем записи из таблицы Pass по ID_Pass и сортируем их по Score
        pass_entries = db.query(Pass).filter(Pass.ID_Pass == data["ID_Pass"]).order_by(Pass.Score.desc()).all()

        if not pass_entries:
            raise HTTPException(status_code=404, detail="No pass entries found for the given ID_Pass")

        # Формируем результат
        sorted_answers = {
            "ID_Pass": data["ID_Pass"],
            "Answers": {}
        }

        for entry in pass_entries:
            # Получаем название TD
            td_entry = db.query(TD).filter(TD.ID_TD == entry.TD).first()

            if not td_entry:
                raise HTTPException(status_code=404, detail=f"TD entry not found for ID_TD {entry.TD}")

            score = entry.Score
            td_name = td_entry.Name

            # Преобразовать числовой Score в текстовый
            text_score = score_to_text.get(score)
            if text_score is None:
                raise HTTPException(status_code=500, detail=f"Invalid score {score} for entry {entry}")

            # Вложить TD_Name в соответствующий text_score
            if text_score not in sorted_answers["Answers"]:
                sorted_answers["Answers"][text_score] = []

            sorted_answers["Answers"][text_score].append(td_name)

        # Преобразовать структуру к нужному формату
        formatted_answers = {"ID_Pass": sorted_answers["ID_Pass"]}
        for text_score, td_names in sorted_answers["Answers"].items():
            formatted_answers[text_score] = {"TD_Names": td_names}

        return formatted_answers

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sorted answers: {str(e)}")

    finally:
        db.close()

@app.get("/popular_tests")
async def get_popular_tests():
    db: Session = SessionLocal()
    try:
        # Запрос для получения количества прохождений для каждой Special
        popular_tests_query = db.query(
            Pass.Special,
            Special.Name,
            func.count(History.ID_Pass).label('pass_count')
        ).join(History, Pass.ID_Pass == History.ID_Pass) \
        .join(Special, Pass.Special == Special.ID_Special) \
        .group_by(Pass.Special, Special.Name) \
        .order_by(func.count(History.ID_Pass).desc()) \
        .all()

        if not popular_tests_query:
            raise HTTPException(status_code=404, detail="No tests found")

        # Формируем результаты
        popular_tests_data = [
            {
                "Special_ID": special_id,
                "Special_Name": special_name,
                "Pass_Count": pass_count
            }
            for special_id, special_name, pass_count in popular_tests_query
        ]

        return popular_tests_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch popular tests: {str(e)}")