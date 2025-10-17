package com.project.dine.right.jdbc.repositories;

import com.project.dine.right.jdbc.models.UserData;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface UserDataRepository extends CrudRepository<UserData, Long> {
    @Query("select * from public.UserData where email=:email and password=:password")
    UserData getUserDataByEmailAndEncryptedPassword(@Param("email") String email, @Param("password") String encryptedPassword);

    @Query("select * from public.UserData where email=:email")
    UserData getUserDataByEmail(@Param("email") String email);

    @Query("select * from public.UserData where user_id=:userId")
    UserData getUserDataById(@Param("userId") Long userId);
}
