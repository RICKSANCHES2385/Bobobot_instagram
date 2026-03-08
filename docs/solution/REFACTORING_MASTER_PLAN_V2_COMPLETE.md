# 🏗️ МАСТЕР-ПЛАН РЕФАКТОРИНГА V2.0 - ПОЛНОЕ ПОКРЫТИЕ 100%

> **ОБНОВЛЕНО:** 2026-03-08  
> **Версия:** 2.0 - Полное покрытие функционала  
> **Статус:** Готов к реализации

## 🎯 КРИТИЧЕСКИЕ ОБНОВЛЕНИЯ V2.0

### Что добавлено:
1. ✅ **6 новых Use Cases** для Instagram Integration
2. ✅ **Новые Value Objects** (HighlightId, CommentId, etc.)
3. ✅ **Расширенный ContentType** enum
4. ✅ **Детальные примеры кода** для всех Use Cases
5. ✅ **100% покрытие** всего функционала оригинального бота

### Покрытие:
- **V1.0:** 90% (40 Use Cases)
- **V2.0:** 100% (46 Use Cases) ✅

---

## 📋 ОГЛАВЛЕНИЕ

1. [Обзор изменений V2.0](#обзор-изменений-v20)
2. [Instagram Integration Context - ОБНОВЛЕНО](#instagram-integration-context-обновлено)
3. [Новые Use Cases - Детальное описание](#новые-use-cases)
4. [Обновленная структура проекта](#обновленная-структура-проекта)
5. [Примеры реализации](#примеры-реализации)
6. [Обновленный план миграции](#обновленный-план-миграции)

---

## 1. ОБЗОР ИЗМЕНЕНИЙ V2.0

### 🆕 Добавленные Use Cases (6 шт):

#### Instagram Integration Context:
1. **FetchInstagramHighlightsUseCase** - получение списка highlights
2. **FetchInstagramHighlightStoriesUseCase** - получение stories из highlight
3. **FetchInstagramFollowersUseCase** - бесплатный просмотр подписчиков
4. **FetchInstagramFollowingUseCase** - бесплатный просмотр подписок
5. **FetchInstagramCommentsUseCase** - получение комментариев к посту
6. **FetchInstagramTaggedPostsUseCase** - получение отмеченных постов

### 🆕 Добавленные Value Objects (8 шт):

```python
# Highlights
- HighlightId
- HighlightTitle
- HighlightCoverUrl

# Comments
- CommentId
- CommentText
- CommentAuthor

# Lists
- FollowersList
- FollowingList
```

### 🔄 Обновленные Enums:

```python
class ContentType(str, Enum):
    STORY = "STORY"
    POST = "POST"
    REEL = "REEL"
    HIGHLIGHT = "HIGHLIGHT"        # ✅ Добавлено
    TAGGED_POST = "TAGGED_POST"    # ✅ Добавлено
```

---

## 2. INSTAGRAM INTEGRATION CONTEXT - ОБНОВЛЕНО

### 2.1 Полный список Use Cases (11 шт):

#### Базовые (5 - было в V1.0):
1. ✅ FetchInstagramProfileUseCase
2. ✅ FetchInstagramStoriesUseCase
3. ✅ FetchInstagramPostsUseCase
4. ✅ FetchInstagramReelsUseCase
5. ✅ SearchInstagramUsersUseCase

#### Новые (6 - добавлено в V2.0):
6. 🆕 FetchInstagramHighlightsUseCase
7. 🆕 FetchInstagramHighlightStoriesUseCase
8. 🆕 FetchInstagramFollowersUseCase
9. 🆕 FetchInstagramFollowingUseCase
10. 🆕 FetchInstagramCommentsUseCase
11. 🆕 FetchInstagramTaggedPostsUseCase

---

### 2.2 Обновленные Value Objects

#### Базовые (было в V1.0):
```python
@dataclass(frozen=True)
class InstagramUsername(BaseValueObject):
    value: str
    
    def _validate(self) -> None:
        if not self.value or len(self.value) < 1:
            raise ValueError("Username cannot be empty")
        if not self.value.replace("_", "").replace(".", "").isalnum():
            raise ValueError("Invalid username format")

@dataclass(frozen=True)
class InstagramUserId(BaseValueObject):
    value: str
    
    def _validate(self) -> None:
        if not self.value or not self.value.isdigit():
            raise ValueError("Invalid Instagram user ID")

@dataclass(frozen=True)
class ProfileStatistics(BaseValueObject):
    followers_count: int
    following_count: int
    posts_count: int
    
    def _validate(self) -> None:
        if self.followers_count < 0 or self.following_count < 0 or self.posts_count < 0:
            raise ValueError("Statistics cannot be negative")

@dataclass(frozen=True)
class Bio(BaseValueObject):
    text: str
    
    def _validate(self) -> None:
        if len(self.text) > 150:
            raise ValueError("Bio too long")

@dataclass(frozen=True)
class ProfilePicture(BaseValueObject):
    url: str
    
    def _validate(self) -> None:
        if not self.url.startswith(("http://", "https://")):
            raise ValueError("Invalid URL")
```

#### 🆕 Новые Value Objects (V2.0):

```python
# Highlights
@dataclass(frozen=True)
class HighlightId(BaseValueObject):
    """Highlight identifier."""
    value: str
    
    def _validate(self) -> None:
        if not self.value or not self.value.isdigit():
            raise ValueError("Invalid highlight ID")

@dataclass(frozen=True)
class HighlightTitle(BaseValueObject):
    """Highlight title."""
    value: str
    
    def _validate(self) -> None:
        if not self.value or len(self.value) > 100:
            raise ValueError("Invalid highlight title")

@dataclass(frozen=True)
class HighlightCoverUrl(BaseValueObject):
    """Highlight cover image URL."""
    url: str
    
    def _validate(self) -> None:
        if not self.url.startswith(("http://", "https://")):
            raise ValueError("Invalid URL")

# Comments
@dataclass(frozen=True)
class CommentId(BaseValueObject):
    """Comment identifier."""
    value: str
    
    def _validate(self) -> None:
        if not self.value:
            raise ValueError("Comment ID cannot be empty")

@dataclass(frozen=True)
class CommentText(BaseValueObject):
    """Comment text content."""
    text: str
    
    def _validate(self) -> None:
        if len(self.text) > 2200:  # Instagram limit
            raise ValueError("Comment text too long")

@dataclass(frozen=True)
class CommentAuthor(BaseValueObject):
    """Comment author information."""
    username: InstagramUsername
    user_id: InstagramUserId
    profile_pic_url: str

# Lists
@dataclass(frozen=True)
class FollowersList(BaseValueObject):
    """List of followers with pagination."""
    users: List[Dict[str, Any]]
    cursor: str | None
    has_more: bool
    total_count: int
    
    def _validate(self) -> None:
        if self.total_count < 0:
            raise ValueError("Total count cannot be negative")
        if self.total_count < len(self.users):
            raise ValueError("Total count cannot be less than users count")

@dataclass(frozen=True)
class FollowingList(BaseValueObject):
    """List of following with pagination."""
    users: List[Dict[str, Any]]
    cursor: str | None
    has_more: bool
    total_count: int
    
    def _validate(self) -> None:
        if self.total_count < 0:
            raise ValueError("Total count cannot be negative")
        if self.total_count < len(self.users):
            raise ValueError("Total count cannot be less than users count")
```

#### 🔄 Обновленный ContentType:

```python
class ContentType(str, Enum):
    """Type of Instagram content."""
    STORY = "STORY"
    POST = "POST"
    REEL = "REEL"
    HIGHLIGHT = "HIGHLIGHT"        # 🆕 Добавлено
    TAGGED_POST = "TAGGED_POST"    # 🆕 Добавлено
    COMMENT = "COMMENT"            # 🆕 Добавлено
```

---

### 2.3 Обновленные Domain Events

#### Базовые (было в V1.0):
```python
@dataclass(frozen=True)
class ProfileDataFetched(DomainEvent):
    profile_id: InstagramUserId
    username: InstagramUsername
    fetched_by: UserId

@dataclass(frozen=True)
class ProfileNotFound(DomainEvent):
    username: InstagramUsername
    requested_by: UserId

@dataclass(frozen=True)
class ProfileIsPrivate(DomainEvent):
    username: InstagramUsername
    requested_by: UserId

@dataclass(frozen=True)
class RateLimitExceeded(DomainEvent):
    user_id: UserId
    limit_type: str  # "per_minute" or "per_day"
```

#### 🆕 Новые Events (V2.0):

```python
@dataclass(frozen=True)
class HighlightsDataFetched(DomainEvent):
    """Highlights data fetched successfully."""
    profile_id: InstagramUserId
    username: InstagramUsername
    highlights_count: int
    fetched_by: UserId

@dataclass(frozen=True)
class HighlightStoriesDataFetched(DomainEvent):
    """Highlight stories data fetched successfully."""
    highlight_id: HighlightId
    stories_count: int
    fetched_by: UserId

@dataclass(frozen=True)
class FollowersDataFetched(DomainEvent):
    """Followers data fetched successfully."""
    profile_id: InstagramUserId
    followers_count: int
    fetched_by: UserId

@dataclass(frozen=True)
class FollowingDataFetched(DomainEvent):
    """Following data fetched successfully."""
    profile_id: InstagramUserId
    following_count: int
    fetched_by: UserId

@dataclass(frozen=True)
class CommentsDataFetched(DomainEvent):
    """Comments data fetched successfully."""
    media_id: str
    comments_count: int
    fetched_by: UserId

@dataclass(frozen=True)
class TaggedPostsDataFetched(DomainEvent):
    """Tagged posts data fetched successfully."""
    profile_id: InstagramUserId
    posts_count: int
    fetched_by: UserId
```

---

## 3. НОВЫЕ USE CASES - ДЕТАЛЬНОЕ ОПИСАНИЕ

### 3.1 FetchInstagramHighlightsUseCase

**Цель:** Получить список highlights профиля

**Файл:** `src/application/instagram_integration/use_cases/fetch_instagram_highlights_use_case.py`

