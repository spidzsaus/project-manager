# Запуск сервера

- Скачайте Python 3.12.4
- Из папки проекта запустите команду `pip install -r requirements.txt` для установки необходимых зависимостей
- Запустите `py manage.py runserver` для поднятия сервера

# Контрибьютинг

## Инициализация репозитория

- Если вы член команды на гите, склонируйте репозиторий `git clone https://github.com/spidzsaus/project-manager`
- `cd project-manager`

## Загрузка изменений

После того как вы изменили репозиторий, чтобы сохранить изменения в общем репозитории проекта, сделайте следующее:

- `git add *` Добавление всех новых файлов
- `git commit -a -m "Описание коммита"`
- `git push origin master`

# Описание структуры проекта

Если разделять внутреннюю архитектуру проекта на основные составляющие, то можно выделить три основных слоя: 
- База данных 
- Логика проекта (сущности, взаимодействия между ними)
- Представление (Джанго, непосредственная обработка URL запросов) 


## Логика проекта
Логику проекта можно описать как взаимодействие определённых сущностей между собой. Основными сущностями в нашем проекте на данный момент являются Проекты, Задачи и Пользователи. У каждой задачи есть один проект, частью которого она является. У каждого пользователя есть несколько проектов, в команде разработки которых он состоит. У каждой задачи есть один или несколько пользователей, которым эта задача назначена. 

Данные сущности в проекте представлены в виде классов, чтобы можно было работать с ними используя ООП. 
Эти классы описаны в файлах в папке `projectsapp/entities/`. У каждого объекта сущности есть свой уникальный ID. 

Так же за каждой сущностью закреплена отдельная таблица в базе данных. Там хранятся все сущности и их данные. Техническое описание этих таблиц содержится в файле `projectsapp/models.py`. 

Доступ к этим таблицам осуществляется через отдельный класс `Repo`. Это нужно для того, чтобы инкапсулировать (изолировать от остального кода) эту довольно техническую и низкоуровневую часть проекта, во избежание путаницы и непредвиденных ситуаций. В `Repo` описаны все необходимые методы для работы с бд, которые принимают на вход объекты сущностей и возвращают объекты сущностей, таким образом работая с `Repo` не приходится парится о тонкостях генерации запросов в бд. 

Например, код, который переименует задачу с определённым ID будет выглядеть так:

```py
# task_id -- данный id задачи, которую мы хотим переимееновать

repo = Repo() 
task = repo.get_task_by_id(task_id) 
task.name = "новое название"
repo.update_task(task)
```

`repo = Repo()` — создание объекта класса Repo для доступа к бд.
`task = repo.get_task_by_id(task_id)` — получение из бд Задачи с заданным id
`task.name = "новое название"` — просто меняем значение поля полученного объекта Задачи
`repo.update_task(task)` — имея обновлённый объект Задачи, заливаем объект с новыми данными обратно в базу данных. (иначе изменения не сохранятся! )

Так же для реализации логики взаимодействий у классов сущностей есть удобные методы. 
Например, код, который добавит пользователя с id = user_id в проект с id = project_id будет выглядеть так:

```py
repo = Repo()

user = repo.get_user_by_id(user_id)
project = repo.get_project_by_id(project_id)

project.add_user(user)
```

Я постарался в классах сущностей и классе `Repo` расписать описания всех методов. Если чего-то будет не хватать — пишите мне или попробуйте реализовать новые методы сами. 

## База данных 

Для взаимодействия с базой данных в проекте используется встроенный функционал Джанго для реализации ORM. Если в двух словах, то это способ генерировать запросы в базу данных не прописывая их напрямую на языке СУБД, а применяя ООП подход.
> От Ивана: Это та часть проекта, которую я хотел бы взять целиком на себя, но могут возникнуть сиутации, когда для реализации какой-то фичи нужно будет, например, добавить в какую-то таблицу новый столбец данных.

Таблицы базы данных описаны через классы моделей ORM в файле `projectsapp/models.py`.
> Подробнее: 
> - https://docs.djangoproject.com/en/5.1/topics/db/models/
> - https://metanit.com/python/django/5.1.php (на русском)

## Представление

Код, наподобие того, который представлен примерами в разделе "Логика проекта", скорее всего, будет писаться в __обработчиках запросов__. 

Принцип взаимодействия проекта с пользователем такой: проект работает на отдельном сервере, пользователь обращается к нему, посылая ему HTTP запросы, проект их обрабатывает, выполняет определённую логику, возможно делает изменения данных в базе данных, и возвращает пользователю либо HTML страничку, которая рендерится в его браузере, либо какие-то данные. 

Обработка запросов пишется в файле `projectsapp/views.py`. За каждый URL запроса отвечает отдельная функция, которая принимает на вход данные запроса пользователя. В `projectsapp/urls.py` прописываются соответствия между URL и функциями-обработчиками, чтобы проект знал, в ответ на какой URL какую функцию вызывать. 
> Подробнее: 
> - https://docs.djangoproject.com/en/5.1/topics/http/views
> - https://metanit.com/python/django/3.1.php (на русском)

HTML странички хранятся в папке `templates/`. Это не совсем обычные HTML — в Джанго есть так называемый "язык шаблонов". По сути, это способ генерировать HTML на ходу. Самый частый пример использования этой фичи — подстановка конкретных значений в текст странички. Например, чтобы в текст странички вставить название какого-то проекта, можно написать `{{ project.name }}` и в функции обработчике передать функции `render` дополнительный аргумент `{"project": project}`, где `project` — переменная в коде, хранящая объект нужного проекта. 
> Подробнее: 
> - https://docs.djangoproject.com/en/5.1/topics/templates/
> - https://metanit.com/python/django/2.1.php (на русском)

