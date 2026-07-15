from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that uses matricule instead of username.
    """
    username_field = User.USERNAME_FIELD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField()
        self.fields['password'] = serializers.CharField()

    def validate(self, attrs):
        matricule = attrs.get(self.username_field, '').strip().upper()
        password = attrs.get('password')

        if matricule and password:
            user = User.objects.filter(matricule=matricule).first()
            if user and user.check_password(password):
                if not user.is_active:
                    raise serializers.ValidationError("Ce compte est désactivé.")
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh = RefreshToken.for_user(user)
                data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': {
                        'id': user.id,
                        'matricule': user.matricule,
                        'email': user.email,
                        'role': user.role,
                        'nom': user.get_full_name(),
                    }
                }
                return data
            raise serializers.ValidationError("Matricule ou mot de passe incorrect.")
        raise serializers.ValidationError("Matricule et mot de passe requis.")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'matricule', 'email', 'role', 'first_name', 'last_name', 'telephone', 'is_active')
        read_only_fields = ('id',)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('matricule', 'email', 'role', 'first_name', 'last_name', 'telephone', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['matricule'] = validated_data['matricule'].strip().upper()
        user = User(**validated_data)
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        try:
            validate_password(password, user)
        except ValidationError as e:
            raise serializers.ValidationError({'password': e.messages})
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            if attr == 'matricule' and value:
                value = value.strip().upper()
            setattr(instance, attr, value)
        if password:
            from django.contrib.auth.password_validation import validate_password
            from django.core.exceptions import ValidationError
            try:
                validate_password(password, instance)
            except ValidationError as e:
                raise serializers.ValidationError({'password': e.messages})
            instance.set_password(password)
        instance.save()
        return instance
