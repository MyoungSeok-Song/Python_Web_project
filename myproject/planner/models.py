from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password


# Create your models here.
# 1) 회원 테이블
class Signup(models.Model):
    email = models.EmailField(primary_key=True)
    password = models.CharField(max_length=100)
    name = models.CharField(max_length=50)
    birth = models.DateField(null=True, blank=True)
    addr = models.CharField(max_length=200, blank=True)
    phone_num = models.CharField(max_length=20, blank=True)

    # 회원 활성화 여부: True이면 활성, False이면 비활성 (탈퇴한 상태)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email

    # 편의를 위해 set_password 메서드를 추가할 수도 있습니다.
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

# 2) 여행 일정 테이블
class Planner(models.Model):
    plan_no = models.AutoField(primary_key=True)
    region = models.CharField(max_length=100, blank=True)
    plan_img = models.CharField(max_length=200, blank=True)  # 이미지 경로 또는 파일명
    sdate = models.DateField(null=True, blank=True)
    edate = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Planner {self.plan_no} - {self.region}"

# 3) 관광지 정보 테이블
class Tourlist(models.Model):
    title = models.CharField(max_length=200, primary_key=True)
    addr1 = models.CharField(max_length=200, blank=True)
    areacode = models.IntegerField(null=True, blank=True)
    sigungucode = models.IntegerField(null=True, blank=True)
    image2 = models.CharField(max_length=200, blank=True)
    readcount = models.IntegerField(default=0)
    ping = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title

# 4) 일정 상세 테이블
class PlannerDetail(models.Model):
    plan_name = models.CharField(max_length=200, primary_key=True)  # 상세 일정 제목 (예: "1일차 계획")
    planner = models.ForeignKey(Planner, on_delete=models.CASCADE)
    signup = models.ForeignKey(Signup, on_delete=models.CASCADE)
    title = models.ForeignKey(Tourlist, on_delete=models.CASCADE)
    wdate = models.DateField(null=True, blank=True)
    memo = models.TextField(blank=True)

    def __str__(self):
        return self.plan_name

# 게시판 기능
from django.db import models
from django.utils import timezone

# 게시판 기능
class Board(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    # 작성자는 Signup 모델과 FK 관계로 연결 (비로그인 시 작성 불가)
    author = models.ForeignKey('Signup', on_delete=models.CASCADE)
    # 좋아요 기능: Signup 모델과의 다대다 관계
    # (한 사용자가 여러 게시물을 좋아할 수 있고, 한 게시물을 여러 사용자가 좋아할 수 있음)
    likes = models.ManyToManyField('Signup', related_name='liked_boards', blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def total_likes(self):
        """게시물의 총 좋아요 수를 반환합니다."""
        return self.likes.count()

    def is_liked_by(self, user):
        """
        특정 사용자가 이 게시물을 좋아요 했는지 여부를 반환합니다.
        템플릿이나 뷰에서 좋아요 상태를 확인할 때 유용합니다.
        """
        return self.likes.filter(pk=user.pk).exists()

    def toggle_like(self, user):
        """
        특정 사용자의 좋아요를 토글합니다.
        이미 좋아요한 경우에는 좋아요를 제거하고, 그렇지 않으면 좋아요를 추가합니다.
        
        :param user: 좋아요를 수행할 Signup 모델 인스턴스
        :return: 좋아요가 추가되었으면 True, 제거되었으면 False를 반환합니다.
        """
        if self.is_liked_by(user):
            self.likes.remove(user)
            return False  # 좋아요가 제거됨
        else:
            self.likes.add(user)
            return True   # 좋아요가 추가됨

    def __str__(self):
        return self.title


# 댓글 기능
class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    board = models.ForeignKey('Board', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(Signup, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment {self.id} by {self.author.email}"

